from flask_restx import Resource
from flask import jsonify
from flask_api import status as _status

class Index(Resource):
    """
    Index endpoint: AnonymousUser allowed; just to check server is running
    """
    def get(self):
        return jsonify({
                "status": _status.HTTP_200_OK,
                "message": "fetched successfully",
            })
