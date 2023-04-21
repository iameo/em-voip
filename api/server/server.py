from flask_restx import Resource
from flask import jsonify
from flask_api import status as _status
from flask_jwt_extended import jwt_required, get_jwt_identity
from routes.restx_loader import restx_api

class Index(Resource):
    @restx_api.doc(security="Bearer")
    @jwt_required()
    def get(self):
        """ Index endpoint: authenticared users only; checks server is running"""
        return jsonify({
                "status": _status.HTTP_200_OK,
                "message": "fetched successfully",
                "extra": get_jwt_identity()
            })
