from flask import request
from db import db_field, db_save
from model.response import response_model
from flask_restx import Resource, Namespace

import bcrypt
import os

from utils.exts import random_label

from datetime import datetime

from flask_restx.reqparse import RequestParser
from flask_restx.inputs import email


auth_ns = Namespace(name="auth", validate=True)

users_index = os.getenv('USERS_INDEX', 'users')



auth_reqparser = RequestParser(bundle_errors=True)
auth_reqparser.add_argument(
    name="email", type=email(), location="form", required=True, nullable=False
)
auth_reqparser.add_argument(
    name="password", type=str, location="form", required=True, nullable=False
)


auth_reqparser_reg = RequestParser(bundle_errors=True)
auth_reqparser_reg.add_argument(
    name="email", type=email(), location="form", required=True, nullable=False
)
auth_reqparser_reg.add_argument(
    name="password", type=str, location="form", required=True, nullable=False
)
auth_reqparser_reg.add_argument(
    name="name", type=str, location="form", required=True, nullable=False
)

def allow_login(json_data):
    # print("000000000")
    email =  request.form.get('email', json_data.get_json().get('email'))
    password = request.form.get('password', json_data.get_json().get('password'))
    

    response = db_field(index=users_index, field='email', value=email)
    if response:
        response_ = response[0]
        check_password = bcrypt.checkpw(password=password.encode('utf8'), hashed_password=response[0]['password'].encode('utf8'))
        if check_password:
            from flask_jwt_extended import create_access_token

            access_token = create_access_token(identity={
                'name': response_['account_data'].get('name'),
                'email': response_.get('email'),
                'user_id': response_.get('user_id'),
                'account_id': response_['account_data'].get('account_id')
            }, expires_delta=False)

            data = {
                'token': access_token,
                'email': response_.get('email'),
                'status': 200,
                'message': 'User found.',
                'kw': response_
            }
            return data
        return {"data":{}, "message":"user could not be validated. kindly check the password and try again", "status":401}
    return {"data":{}, "message":"this user could not be found. kindly check the email and try again", "status":404}


class AllowLogin(Resource):
    @auth_ns.expect(auth_reqparser)
    def post(self):
        auth_data = request
        resp = allow_login(auth_data)
        status = str(resp.pop('status'))
        if '200' in status:
            return response_model(allow_only_data=True, response=resp)
        return response_model(response=resp, explicit_message='User could not be found')



def register_user(json_data):
    
    email =  request.form.get('email', json_data.get_json().get('email'))
    password = request.form.get('password', json_data.get_json().get('password'))
    b_password = password.encode('utf8')
    name = request.form.get('name', json_data.get_json().get('name'))

    response = db_field(index=users_index, field='email', value=email)

    if response:
        status = f"{email} has already been registered. Kindly login if this is your account"
    else:
        from flask_jwt_extended import create_access_token

        account_id = random_label(prefix="account", n=18)
        user_id = random_label(prefix='user', n=18)
        salt = bcrypt.gensalt()
        
        access_token = create_access_token(identity={
                    'name': name,
                    'email': email,
                    'user_id': user_id,
                    'account_id': account_id
                }, expires_delta=False)

        _password = bcrypt.hashpw(b_password, salt)

        current_time = datetime.now()

        data = {
            "status": "active",
            "email": email,
            "password": _password.decode("utf-8"),
            "account_data":{
                "name": name,
                "account_id": account_id,
                "user_id": user_id,
                "photo_url": "",
                "created": current_time,
                "account_type": "free",
                "modified": current_time,
                "token": access_token,
                "role_type": "user",
                
            }
        }
        status = db_save(index=users_index, user_id=user_id, account_id=account_id, json_data=data)
    return {'response': status}


class AllowRegister(Resource):
    @auth_ns.expect(auth_reqparser_reg)
    def post(self):
        data = request
        # print(request.form['email'], "DDDDdddddddddd")
        resp = register_user(data)
        return response_model(allow_only_data=True, response=resp) 