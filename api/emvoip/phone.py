from flask import request, jsonify
from flask_api import status as _status
from flask_restx import Resource
from services.emvoip.phone import Phone

from model.response import response_model
from routes.restx_loader import ns, restx_api
from flask_restx.reqparse import RequestParser

from flask_jwt_extended import get_jwt_identity, jwt_required

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
    @jwt_required()
    def post(self):
        '''provision a phone number'''
        json_data = request.get_json()
        response = phone_api.new_phone_detail(json_data=json_data, user_id=get_jwt_identity()['user_id'], account_id=get_jwt_identity()['account_id'])
        return response_model(response=response, allow_only_data=True)



#argparser
limit_reqparser = RequestParser(bundle_errors=True)
limit_reqparser.add_argument(
    name="limit", type=str, location="args", required=False, nullable=True
)


class PurchasedNumbers(Resource):
    @restx_api.expect(limit_reqparser)
    @jwt_required()
    def get(self):
        '''view all purchased numbers'''
        n = request.args.get('limit', None)
        account_id = get_jwt_identity()['account_id']
        purchased_numbers = phone_api.purchased_numbers(n, account_id=account_id)
        return response_model(response=purchased_numbers, allow_only_data=True)



class Address(Resource):
    @jwt_required()
    def post(self):
        address_data = request.get_json()
        account_id = get_jwt_identity()['account_id']
        results = phone_api.add_address(address_data, account_id)
        return response_model(response=results, allow_only_data=True)

    @jwt_required()
    def get(self):
        account_id = get_jwt_identity()['account_id']
        results = phone_api.addresses(account_id)
        return response_model(response=results, allow_only_data=True)
