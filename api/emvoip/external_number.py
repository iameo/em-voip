from services.emvoip.external_phone_services import request_ext_countries
from flask import jsonify
from flask_restx import Resource

from model.response import response_model


class RequestCountriesForExternalNumber(Resource):
    def get(self):
        result_list = request_ext_countries()
        return response_model(result_list, explicit_message="fetched successfully", allow_only_data=True)