from model.response import response_model
from services.emvoip.communication_services import TwilioCommClient
from flask_restx import Resource

from services.middlewares.common import route_protector
from flask_jwt_extended import get_jwt_identity



@route_protector(None)
def twilio_init(throw_identity=False):   
    account_id = get_jwt_identity()['account_id']
    user_id = get_jwt_identity()['user_id']
    twilio_client = TwilioCommClient(account_id, user_id)
    if throw_identity:
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

