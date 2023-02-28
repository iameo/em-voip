from flask_jwt_extended import get_jwt_identity
from functools import wraps
from twilio.base.exceptions import TwilioRestException, TwilioException
from twilio.rest import Client as TwilioClient


from utils.communication.phone import get_account
from services.middlewares.common import route_protector

import os


dev_mode_ = os.getenv('DEV_MODE_TWILIO', False)



def auth_checker(twilio_func, dev_mode=dev_mode_):
    """
    decorator to catch errors on existing twilio functions/methods, without\
    manual try-except blocks

    dev_mode: True if you need to know affected twilio method/function decorated and error message
    """
    
    func_name = twilio_func.__name__ if dev_mode else ""

    @wraps(twilio_func)
    def inner_func(*args, **kwargs):
        try:
            result = twilio_func(*args, **kwargs)
        except TwilioException as e:
            return {'status':401, 'message':f"Invalid authentication credentials. {func_name}: Error: {str(e)}"}
        except TwilioRestException as e:
            return {'status':500, 'message': f"We could not authenticate you at this time. Your credit might be running low. {func_name}: Error: {str(e)}"}
        except Exception as e:
            return {'status': 504, 'message':f"Something went wrong. Please try again later. {func_name}: Error: {str(e)}"}
        return result
    return inner_func


@route_protector(None)
def initialize_client(account_dict=True):
    """
    Initialize a twilio client
     - returns a twilio client, its associated account sid, its associated auth_token

    args:
        account_dict: a dictionary with a twilio client credentials
    """
    if not account_dict:
        account_id = get_jwt_identity()['account_id']
        account = get_account(lookup={"account_id":account_id})

        try:
            twilio_account_sid = account[0].get('twilio_account_sid')
            twilio_auth_token = account[0].get('twilio_auth_token')
        except IndexError:
            return (None, None, None)

    if account_dict:
        twilio_account_sid = account_dict.get('twilio_account_sid')
        twilio_auth_token = account_dict.get('twilio_auth_token')


    client = TwilioClient(twilio_account_sid, twilio_auth_token) 
    return client, twilio_account_sid, twilio_auth_token
