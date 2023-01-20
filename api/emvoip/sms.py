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
    @route_protector(None)
    def get(self):
        twilio_client, identity = twilio_init(include_identity=True)
        token =  twilio_client.get_twilio_token(identity=identity)
        return response_model(response=token, allow_only_data=True)


class SendSMS(Resource):
    def post(self):
        twilio_client = twilio_init()
        return twilio_client.voice()

    def lock(self):
        sms_data = request.get_json()
        print("sms data: ", sms_data)
        twilio_client = twilio_init()
        return twilio_client.send_sms(sms_data)