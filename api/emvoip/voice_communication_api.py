from http import client
from model.response import response_model
from services.emvoip.communication_services import TwilioCommClient
from flask_restx import Resource

from services.middlewares.common import route_protector
from flask_jwt_extended import get_jwt_identity
from flask import request



@route_protector(None)
def twilio_init(include_identity=False, block_twilio_client=False):   
    account_id = get_jwt_identity()['account_id']
    user_id = get_jwt_identity()['user_id']
    twilio_client = TwilioCommClient(account_id, user_id, block_twilio_client)
    if include_identity:
        return twilio_client, user_id
    return twilio_client


class TwilioToken(Resource):
    def get(self):
        twilio_client, identity = twilio_init(throw_identity=True)
        token =  twilio_client.get_twilio_token(identity=identity)
        return response_model(response=token, allow_only_data=True)


class Voice(Resource):
    def post(self):
        twilio_client = twilio_init()
        return twilio_client.voice()


class HandleCall(Resource):
    def post(self):
        to = request.values.get('To')
        call_status = request.values.get('CallStatus')
        caller_country = request.values.get('CallerCountry')

        twilio_client = twilio_init(block_twilio_client=True)
        return twilio_client.handle_call(to=to, call_status=call_status, country=caller_country)


class EndCall(Resource):
    def post():
        """ resource to end ongoing call
    
        initialize VoiceResponse
        hangup on the instance
        return xml response of the instance to complete TWIML instructions
        """
        from twilio.twiml.voice_response import VoiceResponse
        from flask import Response

        twiml = VoiceResponse()
        twiml.hangup()
        return Response(str(twiml), mimetype='application/xml')
