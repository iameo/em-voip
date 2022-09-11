import mimetypes
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, request, Response
from twilio.rest import Client as TwilioClient
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial

from utils.twilio_supported_langs import available_langs
from services.middlewares.common import route_protector




def get_account(index="", *, lookup=None):
    key, value = lookup.popitem()
    return key, value

# @route_protector(None)
def initialize_client(account_dict=None):
    if not account_dict:
        account_id = 'ld' or get_jwt_identity()['account_id']
        account = get_account(lookup={"account_id":account_id})
    
    if account_dict or account:
        return TwilioClient('rr' or account['twilio_account_sid'], 'de' or account['twilio_auth_token'])
    
    return {}

def phone_number_parser(contact, country=None):
    """parses a typical phone number"""
    import phonenumbers
    from phonenumbers.phonenumberutil import NumberParseException
    
    if country is None:
        country = 'US'

    try:
        contact = phonenumbers.parse(contact, country)
    except NumberParseException:
        return str(contact), False
    valid_num = phonenumbers.is_valid_number(contact)
    if valid_num:
        return f"+{contact.country_code}{contact.national_number}", True 
    else:
        return str(contact), False


class TwilioCommClient(object):
    def __init__(self, account_id, user_id):
        self.account_id = account_id
        self.user_id = user_id

        self.account = get_account(lookup={'account_id':self.account_id})
        self.subclient = initialize_client()

    @property
    def fetch_twilio_secrets(self):
        subclient = self.subclient()

        key_secret = subclient.new_keys.create(
            friendly_name=f'{self.account_id}[:15]__{self.user_id}[5]'
        )

        return key_secret
        
    def get_twilio_token(self):
        identity = ''
        twilio_secrets = self.fetch_twilio_secrets()

        if not twilio_secrets:
            print('err')
        
        token = AccessToken(self.account['twilio_account_sid'], self.account['twilio_auth_token'])

        voice = VoiceGrant(
            outgoing_application_sid='',
            incoming_allow=True
        )

        token.add_grant(voice)

        return jsonify(identity=identity, token=token)

    def voice(self):
        twiml = VoiceResponse()

        twilio_account_sid = request.values.get('AccountSid')
        caller_country = request.values.get('CallerCountry')

        caller_lang = self.fetch_caller_lang(caller_country)

        call_recipent = request.form['To']
        caller = request.values.get('From')

        caller_id = caller or request.values.get('Caller')

        events = 'initiated ringing answered completed'
        call_handler_uri = '/call/handle'
        call_event_uri = '/call/events'

        identity = ''

        if caller == call_recipent:
            twiml.hangup()
            return Response(str(twiml), mimetype='application/xml')
        
        if call_recipent in self.subaccount_contacts(twiml, call_recipent, caller_country, caller_lang, limit=4):
            dial = Dial(timeout=15, action=call_handler_uri)
            dial.client(
                identity=identity,
            )

            twiml.append(dial)

            return Response(str(twiml), mimetype='application/xml')
        
        elif call_recipent:
            dial = Dial(caller_id=caller_id)
            dial.number(
                phone_number=call_recipent
            )
            
        else:
            twiml.say('ahhhhhhhhhhhhh')
        
        twiml.append(dial)
        return Response(str(twiml), mimetype='applicaiton/xml')




    def subaccount_contacts(self, twiml, contact, country, language, limit=2):

        contacts = set()

        contact, contact_validity = self.validate_contact_number(contact.strip(), country=country)
        if not contact_validity:
            twiml.say('The number you are calling is not valid. Please check the number and try again.', loop=2, language=language)
            twiml.hangup()
            return contacts


        subclient = self.subclient()
        account_contact_list = subclient.incoming_phone_numbers.list(
            phone_number=contact, limit=limit
        )

        if account_contact_list:
            contacts = {contact_.phone_number for contact_ in account_contact_list}
        return contacts



    def validate_contact_number(contact, caller_country):
        return phone_number_parser(contact, caller_country)


    def fetch_caller_lang(self, caller_country):
        language = next((key for key in available_langs if key.endswith(str(caller_country))), None)
        language = 'en-US' if language is None else language
        return language