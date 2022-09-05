from email import message
from flask import request, jsonify
from flask_api import status as _status
from flask_restx import Resource
from services.emvoip.phone import Phone

from model.response import response_model
from routes.restx_loader import ns, restx_api

phone_api = Phone()

class PhoneRequestCountries(Resource):
    '''Available countries to purchase a number from at any given time'''
    def get(self):
        response = phone_api.request_countries()
        return response_model(response, allow_only_data=True)

class PhoneRequestPricing(Resource):
    '''Get pricing for any given country'''
    @ns.param('country','check pricing for this country (example: US)')
    def get(self):
        country = request.args.get('country')
        response = phone_api.request_number_pricing(country=country)
        return response_model(response=response)

class PhoneDetail(Resource):
    def post(self):
        '''provision a phone number'''
        json_data = request.get_json()
        response = phone_api.new_phone_detail(json_data=json_data, user_id='', company_id='')
        return response_model(response)



