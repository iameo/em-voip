from flask import jsonify
from flask_api import status as _status
from bson import json_util
import json


def response_model(response=None, explicit_message=None, allow_only_data=False):
    if response and allow_only_data:
        return jsonify(message="fetched successfully", data=_encode_data(response), status=_status.HTTP_200_OK)

    data = response.get('data', {})
    status = response.get('status', _status.HTTP_200_OK)

    if explicit_message:
        message = explicit_message
    else:
        message = response.get('message')

    if not data:
        return jsonify(message="Connection could not be established to get your result. Please try again later", status=_status.HTTP_500_INTERNAL_SERVER_ERROR, data={}, module="VOIP")
    
    if status in range(200, 208) and not message:
        message = "success"
    
    if status == 400:
        status = _status.HTTP_400_BAD_REQUEST
        message = "Bad Request"
    
    if status == 401:
        status = _status.HTTP_401_UNAUTHORIZED
        message = "Unauthorized"
    
    if status == 402:
        status = _status.HTTP_402_PAYMENT_REQUIRED
        message = "Card required"
    
    if status == 403:
        status = _status.HTTP_403_FORBIDDEN
        message = "Access denied"
    
    if status == 404:
        status = _status.HTTP_404_NOT_FOUND
        message = "Resource not found"
    
    if status == 405:
        status = _status.HTTP_405_METHOD_NOT_ALLOWED
        message = "Method not allowed"
    
    if status == 408:
        status = _status.HTTP_408_REQUEST_TIMEOUT
        message = "Request timeout"
    
    if status == 500:
        status = _status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "Internal server error"

    if status == 503:
        status = _status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Service unavailable. Try again later"

    if isinstance(data, dict):
        is_archived = data.get('is_archived')
        if is_archived:
            message = "Resource has been archived"

    return jsonify(data=_encode_data(data), message=message, status=status)


def _encode_data(data):
    return json.loads(json_util.dumps(data))
