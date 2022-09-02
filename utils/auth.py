from flask import jsonify
from functools import wraps
from twilio.base.exceptions import TwilioRestException, TwilioException
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