from flask import render_template
from app import app
from werkzeug.exceptions import HTTPException


@app.errorhandler(HTTPException)
def error_handler(e):
    error_codes = {
    400: ("Bad Request", "The server could not understand the request due to invalid syntax."),
    401: ("Unauthorized", "You must authenticate yourself to get the requested response."),
    403: ("Forbidden", "You do not have permission to access the requested resource."),
    404: ("Not Found", "The requested resource could not be found on the server."),
    405: ("Method Not Allowed", "The HTTP method used is not supported for this resource."),
    408: ("Request Timeout", "The server timed out waiting for the request."),
    409: ("Conflict", "The request could not be completed due to a conflict with the current state of the resource."),
    413: ("Payload Too Large", "The request payload is larger than the server is willing or able to process."),
    415: ("Unsupported Media Type", "The server does not support the media type transmitted in the request."),
    429: ("Too Many Requests", "You have sent too many requests in a given amount of time."),
    500: ("Internal Server Error", "The server encountered a condition that prevented it from fulfilling the request."),
    501: ("Not Implemented", "The server does not recognize the request method, or it lacks the ability to fulfill the request."),
    502: ("Bad Gateway", "The server received an invalid response from the upstream server."),
    503: ("Service Unavailable", "The server is not ready to handle the request. This could be due to maintenance or overload."),
    504: ("Gateway Timeout", "The server did not receive a timely response from the upstream server."),
    }
    title, message = error_codes.get(e.code,'Unknown Error. Please contact admin for further help')
    return render_template('errors.html',title=title,message=message)