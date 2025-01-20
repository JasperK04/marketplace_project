import sqlalchemy as sa
from app.extensions import db, basic_auth, token_auth
from app.models.User import User
from app.api import api
from app.api.errors import error_response


@basic_auth.verify_password
def verify_password(username:str, password:str):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user and user.check_password(password):
        return user


@basic_auth.error_handler
def basic_auth_error(status:int):
    return error_response(status)


@api.route("/tokens", methods=["POST"])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()  # type: ignore
    db.session.commit()
    return {"token": token}, 201


@api.route("/tokens", methods=["DELETE"])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()  # type: ignore
    db.session.commit()
    return "", 204


@token_auth.verify_token
def verify_token(token:str):
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status:int):
    return error_response(status)
