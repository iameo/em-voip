from flask import request
from db import db_field, db_save
from model.response import response_model
from flask_restx import Resource

import bcrypt
import os

from utils.exts import random_label

from datetime import datetime

users_index = os.getenv('USERS_INDEX', 'users')


def allow_login(json_data):
    email = json_data.get('email')
    password = json_data.get('password')

    response = db_field(index=users_index, field='email', value=email)

    if response:
        response_ = response[0]
        check_password = bcrypt.checkpw(password=password.encode('utf8'), hashed_password=response[0]['password'].encode('utf8'))
        if check_password:
            from flask_jwt_extended import create_access_token

            access_token = create_access_token(identity={
                'name': response_['account_data'].get('name'),
                'email': response_.get('email'),
                'user_id': response_.get('user_id')
            }, expires_delta=False)

            data = {
                'token': access_token,
                'email': response_.get('email'),
                'kw': response_
            }

            return data
    return {"data":{}, "message":"failed"}

class AllowLogin(Resource):
    def post(self):
        auth_data = request.get_json()
        resp = allow_login(auth_data)
        return response_model(allow_only_data=True, response=resp)



def register_user(json_data):
    email = json_data.get('email')
    b_password = json_data.get('password').encode('utf-8')

    response = db_field(index=users_index, field='email', value=email)

    if response:
        status = f"{email} has already been registered. Kindly login if this is your account"
    else:
        from flask_jwt_extended import create_access_token

        account_id = random_label(prefix="account", n=18)
        user_id = random_label(prefix='user', n=18)
        salt = bcrypt.gensalt()

        name =  json_data.get('name')
        
        access_token = create_access_token(identity={
                    'name': name,
                    'email': email,
                    'user_id': user_id,
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
    return status


class AllowRegister(Resource):
    def post(self):
        data = request.get_json()
        resp = register_user(data)
        return response_model(allow_only_data=True, response=resp) 