from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES
from . import api


def bad_request(message):
    return error_response(400, message)


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    return payload, status_code


@api.errorhandler(HTTPException)
def handle_exception(e):
    return error_response(e.code)
