from http import client
from model.response import response_model
from services.emvoip.communication_services import TwilioCommClient
from flask_restx import Resource

from services.middlewares.common import route_protector
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import request, jsonify
import jwt


from routes.restx_loader import restx_api

from flask_restx.reqparse import RequestParser




#argparser for swagger and voice endpoint

voice_reqparser = RequestParser(bundle_errors=True)
voice_reqparser.add_argument(
    name="From", type=str, location="form", required=True, nullable=False, default="+19253161405"
)
voice_reqparser.add_argument(
    name="To", type=str, location="form", required=True, nullable=False, default="+2348162575674"
)


transfer_reqparser = RequestParser(bundle_errors=True)
transfer_reqparser.add_argument(
    name="From", type=str, location="form", required=True, nullable=False, default="+19253161405"
)
transfer_reqparser.add_argument(
    name="To", type=str, location="form", required=True, nullable=False, default="+2348162575674"
)

transfer_reqparser.add_argument(
    name="SID", type=str, location="form", required=True, nullable=False, default="+2348162575674"
)
#----- collective parsers end here


@jwt_required()
def twilio_init(include_identity=False, block_twilio_client=False):
    '''
    initialize twilio client by collecting relevant data through JWT
    '''
    account_id = get_jwt_identity()['account_id']
    user_id = get_jwt_identity()['user_id']
    twilio_client = TwilioCommClient(account_id, user_id, block_twilio_client)
    if include_identity:
        return twilio_client, user_id
    return twilio_client


class TwilioToken(Resource):
    @restx_api.doc(security='Bearer')
    def get(self):
        twilio_client, identity = twilio_init(include_identity=True)
        token =  twilio_client.get_twilio_token(identity=identity)
        return response_model(response=token, allow_only_data=True)





#---- voice implementation flow below
class Voice(Resource):
    @restx_api.expect(auth_reqparser)
    @restx_api.doc(security='Bearer')
    @jwt_required()
    def post(self):
        twilio_client = twilio_init()
        return twilio_client.voice()

    @jwt_required()
    def get(self):
        twilio_client = twilio_init()
        return twilio_client.voice()


class HandleCall(Resource):
    def post(self):
        to = request.values.get('To')
        call_status = request.values.get('CallStatus')
        caller_country = request.values.get('CallerCountry')

        twilio_client = twilio_init(block_twilio_client=True)
        return twilio_client.handle_call(to=to, call_status=call_status, country=caller_country)


    def get(self):
        to = request.values.get('To')
        call_status = request.values.get('CallStatus')
        caller_country = request.values.get('CallerCountry')

        twilio_client = twilio_init(block_twilio_client=True)
        return twilio_client.handle_call(to=to, call_status=call_status, country=caller_country)


class EndCall(Resource):
    def post(self):
        """ 
        resource to end ongoing call
    
        initialize VoiceResponse
        hangup on the instance
        return xml response of the instance to complete TWIML instructions
        """
        from twilio.twiml.voice_response import VoiceResponse
        from flask import Response

        twiml = VoiceResponse()
        twiml.hangup()
        return Response(str(twiml), mimetype='application/xml')

    def get(self):
        """ 
        resource to end ongoing call
    
        initialize VoiceResponse
        hangup on the instance
        return xml response of the instance to complete TWIML instructions
        """
        from twilio.twiml.voice_response import VoiceResponse
        from flask import Response

        twiml = VoiceResponse()
        twiml.hangup()
        return Response(str(twiml), mimetype='application/xml')
