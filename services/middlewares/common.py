from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import request
from model.response import response_model
# from services.emvoip.communication_services import initialize_client

def route_protector(index=None, end_point=None, permission=None):
    from db import db_fetch
    
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_identity()
            user_id = claims.get('user_id', None)
            if not user_id:
                return response_model()
            
            account_id = claims.get('user_id')

            if account_id and permission:
                logged_user = db_fetch(index='users', id=user_id)
            
            if not account_id:
                return response_model(explicit_message='account ID missing in url')
            # else:
            #     access, reason, role = {}
            #     if access is False or access is None:
            #         return response_model(explicit_message=str(reason))
            

            id = kwargs.get('id')
            id = user_id if index == 'users' else id

            lead_id = kwargs.get('lead_id')
            pipeline_id = kwargs.get('pipeline_id')

            if lead_id:
                logged_lead = db_fetch(index='leads', id=lead_id)

                if not logged_lead:
                    return response_model(explicit_message='resource may have been moved')
                
                if logged_lead.get('account_id') != account_id:
                    return response_model(explicit_message='access denied. No permission to access this resource') 

                if logged_lead.get('is_delete') == 1:
                    return response_model(explicit_message='resource could not be retrieved') 

            if pipeline_id:
                data = db_fetch(index='pipelines', id=pipeline_id)
                alte(payload=data, index='users', account_id=account_id, check_user=False)

            if id:
                data = db_fetch(index=index, id=id)
                alte(payload=data, index='users', account_id=account_id, check_user=True)
                
                if lead_id:
                    if data.get('lead_id') != lead_id:
                        return response_model(explicit_message='this lead has no access to this resource')

                if pipeline_id:
                    if data.get('pipeline_id') != pipeline_id:
                        return response_model(explicit_message='pipeline mismatch')
                
            return func(*args, **kwargs)
        return decorator
    return wrapper


def alte(payload=None,  index=None, account_id=None, check_user=False):
    if not payload:
        return response_model(explicit_message='resource could not be retrieved')
    
    if payload.get('is_delete') == 1:
        return response_model(explicit_message='permission denied. Resource has been deleted')
    
    if check_user:
        is_user = False
        if index == 'users':
            for datum in payload['account_data']:
                if datum['id'] == account_id and datum['status'] == 1:
                    is_user = True
            if not is_user:
                return response_model(explicit_message='permission denied. you do not have the permission to access this resource')

        else:
            if payload.get('account_id') != account_id:
                return response_model(explicit_message='permission denied. no permission to access this resource on this account ID')
                
   

def clean_payload(value):
    import html
    if isinstance(value, str):
        value = html.escape(value.strip())
    return value

            
        