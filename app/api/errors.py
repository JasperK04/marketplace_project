from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES
from . import api


def bad_request(message: str):
    return error_response(400, message)


def unauthorized(message: str):
    return error_response(401, message)


def not_found(message: str):
    return error_response(404, message)


def error_response(status_code: int, message: str | None = None):
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}
    if message:
        payload["message"] = message
    return payload, status_code


@api.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    if not e.code:
        return error_response(500)
    return error_response(e.code)
