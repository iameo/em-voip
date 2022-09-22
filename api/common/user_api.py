from os import access
from flask import request, jsonify
from db import db_field
from model.response import response_model
from flask_restx import Resource

import bcrypt
import os

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
                'name': response_.get('name'),
                'email': response_.get('email'),
                'user_id': response_
            }, expires_delta=False)

            data = {
                'token': access_token,
                'email': response_.get('email'),
                'kw': response_
            }

            return data
    
    else:
        return {"data":{}, "message":"ailed"}

class AllowLogin(Resource):
    def post(self):
        auth_data = request.get_json()
        resp = allow_login(auth_data)
        return response_model(allow_only_data=True, response=resp)
