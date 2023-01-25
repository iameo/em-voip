import json
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, request, Response
from twilio.rest import Client as TwilioClient
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
from db import db_fetch, db_save
from model.response import response_model

from utils.twilio_supported_langs import available_langs
from utils.communication.phone import _validate_phone
from services.middlewares.common import route_protector

import os




def get_account(index="subaccounts", *, lookup=None):
    key, value = lookup.popitem()
    query = {
            "query": {
            "bool": {
                "must": [
                {
                    "match_phrase": {
                        f"{key}": f"{value}"
                    }
                },
                {
                    "match_phrase": {
                        "is_delete": 0
                    }
                }
                
                ]
            }
            }
        }  
    try:
        account = db_fetch(index=index, query=query)
    except IndexError:
        return None
    return account


def fetch_caller_lang(caller_country):
    language = next((key for key in available_langs if key.endswith(str(caller_country))), None)
    language = 'en-US' if language is None else language
    return language


@route_protector(None)
def initialize_client(account_dict=True):
    if not account_dict:
        account_id = get_jwt_identity()['account_id']
        account = get_account(lookup={"account_id":account_id})
    
    if account_dict or account:
        return TwilioClient(account['twilio_account_sid'], account['twilio_auth_token']) 
    
    return {}



class TwilioCommClient(object):
    def __init__(self, account_id, user_id, block_twilio_client=False):
        self.account_id = account_id
        self.user_id = user_id

        self.BASE_URL = os.getenv("BASEURL_VOIP")
        self.TWILIO_MESSAGING_SERVICE_SID = os.getenv('TWILIO_MESSAGING_SERVICE_SID')

        
        #block_twilio_client set to False if object requires twilio client
        if not block_twilio_client:
            self.account = get_account(lookup={'account_id':self.account_id})
            self.subclient, self.twilio_sid, self.twilio_auth_token = initialize_client()

    @property
    def fetch_twilio_secrets(self):
        friendly_name = f'{str(self.account_id)}'

        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                        "match_phrase": {
                            "friendly_name": friendly_name
                                }
                        },
                        {
                        "match_phrase": {
                            "user_id": self.user_id
                                 }
                    },
                    {
                        "match_phrase": {
                            "is_delete": 0
                        }
                    }
                
                    ]
                }
            }
        }
        existing_key_secret = db_fetch(index='twilio_sid_secretx', query=query)

        if not existing_key_secret:
            subclient = self.subclient

            sid_secret = subclient.new_keys.create(
                friendly_name=friendly_name
            )

            data = {
                'friendly_name': friendly_name,
                'secret': sid_secret.secret,
                'sid': sid_secret.sid
            }
            _ = db_save(index='twilio_sid_secretx', json_data=data, account_id=self.account_id, user_id=self.user_id)
            return data

        key_secret = existing_key_secret[0]
        return {'secret': key_secret.get('secret'), 'sid':key_secret.get('sid')}
        

    def get_twilio_token(self, identity):
        twilio_secrets = self.fetch_twilio_secrets

        if not twilio_secrets:
            return response_model(response={}, explicit_message='SID and SECRET failed to generate')
        

        token = AccessToken(
                    account_sid=self.twilio_sid,
                    signing_key_sid=twilio_secrets.get('sid'),
                    secret=twilio_secrets.get('secret'),
                    identity=identity
                )

        voice = VoiceGrant(
            outgoing_application_sid= os.getenv('TWILIO_TWIML_APP_SID'),
            incoming_allow=True
        )

        token.add_grant(voice)

        return {"identity":identity, "token":token.to_jwt()}


    def voice(self):
        twiml = VoiceResponse()

        twilio_account_sid = request.values.get('AccountSid')
        caller_country = request.values.get('CallerCountry')

        caller_lang = fetch_caller_lang(caller_country)

        call_recipent = request.form['To']
        caller = request.values.get('From')

        caller_id = caller or request.values.get('Caller')

        #voice/accent locale using caller country
        language = fetch_caller_lang(caller_country=caller_country)

        events = 'initiated ringing answered completed' #call events at any given time
        call_handler_uri = '/call/handle'
        # call_event_uri = '/call/events'

        identity = ''

        if caller == call_recipent:
            twiml.hangup()
            return Response(str(twiml), mimetype='application/xml')
        
        if call_recipent in self.subaccount_contacts(twiml, call_recipent, caller_country, caller_lang, limit=4):
            dial = Dial(timeout=15, action=call_handler_uri)
            dial.client(
                identity = identity,
                status_callback_event = events,
                # status_callback = call_event_uri,
                status_callback_method = 'POST',
            )

            twiml.append(dial)

            return Response(str(twiml), mimetype='application/xml')
        
        elif call_recipent:
            contact, contact_valid = _validate_phone(call_recipent, caller_country)

            if not contact_valid:
                twiml.say("The number dialled is not valid. Please Check the number and try again.", language=language)
                twiml.hangup()
                return str(twiml)

            dial = Dial(caller_id=caller_id)
            dial.number(
                phone_number = contact,
                # status_callback_event = events,
                # status_callback = call_event_uri,
                # status_callback_method = 'POST',
            )
            
        else:
            twiml.say('server error. please try again.')
        
        twiml.append(dial)
        return Response(str(twiml), mimetype='applicaiton/xml')




    def subaccount_contacts(self, twiml, contact, country, language, limit=2):

        contacts = set()

        contact, contact_validity = _validate_phone(contact.strip(), country=country)
        if not contact_validity:
            twiml.say('The number you are calling is not valid. Please check the number and try again.', loop=2, language=language)
            twiml.hangup()
            return contact

        subclient = self.subclient
        account_contact_list = subclient.incoming_phone_numbers.list(
            phone_number=contact, limit=limit
        )

        if account_contact_list:
            contacts = {contact_.phone_number for contact_ in account_contact_list}
        return contacts


    def handle_call(self, to, call_status, country):
        """
        action_url receives this as argument, and is triggered when Dial timeout is exhausted\
        
        handles:
            call-forwarding
            voicemail-drop
            voicemail-greeting
            hangup (another action_url trigger)
        """

        response = VoiceResponse()

        is_forward = False
        is_record = False
        is_greeting = False

        language = fetch_caller_lang(caller_country=country)

        if not to:
            response.hangup()
            return Response(str(response), mimetype='application/xml')

        # fetch phones details
        #contact_data = get_by_field(index='phone_details', field='phone_number', value=to, is_delete=0)
        if not contact_data:
            #catch error => hang up the call
            response.say('There was an issue connecting your call at this time. Goodbye!', language=language)
            response.hangup()
            return Response(str(response), mimetype='application/xml')

        # get agent preferences
        contact_data = contact_data[0]
        is_forward = contact_data.get('forward_to_enabled')
        forward_to = contact_data.get('forward_to')
        is_record = contact_data.get('is_record_enabled')
        voicemail_greeting = contact_data.get('voice_greeting_url')
        is_greeting = contact_data.get('voice_greeting_enabled')
        

        """
        call flow logic:

        failed/no-answer and forward_enabled => forward call and hangup (make loop? )
        forward-enabled/busy and greeting enabled => play voicemail greeting, record voicemail and hangup
        busy/no-answer => record voicemail and hangup
        completed => hangup
        other call status options, filtering all the above => hangup
        """
        if (call_status == 'failed' or call_status == "no-answer") and bool(is_forward) and not bool(is_greeting):
            forward_to = contact_data[0]['forward_to']
            response.say("this call will be forwarded to another number, please stay on the line.", language=language)
            response.dial(forward_to, record='record-from-ringing-dual' if bool(is_record) else 'false', action='/call/end')

        elif call_status == 'completed': response.hangup()
        
        elif (bool(is_forward) == False or call_status == "busy" or call_status == 'no-answer') and bool(is_greeting):
            response.play(voicemail_greeting, loop=1)
            response.record(timeout=20,transcribe=True, transcribe_callback="http://twimlets.com/voicemail?Email=emmanuel%40sloovi.com&", play_beep=True)
            response.say("Thanks for your message.", language=language)
            response.hangup()
        
        elif call_status == "busy" or call_status == "no-answer":
            response.say("Hello! we are unable to pick your call right now, please leave a message after the beep.", language=language)
            response.record(
                timeout=20, 
                max_length=20, 
                play_beep=True, 
                trim='trim-silence',
                action=self.BASEURL + '/call/voicemail_action_callback')
            response.hangup() #since going to action, this is not needed but we'll keep
        else:
            response.hangup()

        """
        we need to get the flow of gather to know when to save call data

        update:
            front-end saving call log data
        
        """
        # call_data_to_save(contact_to=forward_to or to, data=request.values)

        return Response(str(response), mimetype='application/xml')


    @staticmethod
    def purchased_numbers():
        subclient = initialize_client()[0]
        numbers_owned = subclient.incoming_phone_numbers.list(limit=5)
        return {'v':numbers_owned}

    
    def check_account_status(self):
        #subclient, _ =  #

        pass


    def send_sms(self, data):
        client = self.subclient
        message = client.messages.create(
            body = data['body'],
            to = data['to'][0]['phone'],
            from_ = data['from'][0]['phone'],
            message_service_sid = self.TWILIO_MESSAGING_SERVICE_SID
        )

        return {'msg': message}