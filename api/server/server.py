from flask_restx import Resource
from flask import jsonify
from flask_api import status as _status
from routes.restx_loader import restx_api
from http import HTTPStatus
from flask_jwt_extended import jwt_required

class Index(Resource):
    @restx_api.doc(security='Bearer')
    @restx_api.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @restx_api.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @jwt_required()
    def get(self):
        return jsonify({
                "status": _status.HTTP_200_OK,
                "status": "fetchedd successfully",
            })
