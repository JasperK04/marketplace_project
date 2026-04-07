"""
This module contains the admin routes for the API
"""

from flask import Blueprint, request, session, url_for
import sqlalchemy as sa
from app.extensions import db
from app.api import api
from app.api.auth import token_auth
from app.api.errors import bad_request, unauthorized, not_found
from app.models.User import User
from app.models.Listing import Listing


admin = Blueprint("admin", __name__)
api.register_blueprint(admin, url_prefix="/admin")


def is_allowed_to_take_admin_action():
    """
    Helper function to check if the user is allowed to take admin actions
    """
    token_user = token_auth.current_user()
    if token_user and token_user.is_admin:  # type: ignore
        return True

    session_user_id = session.get("_user_id")
    if session_user_id is None:
        return False

    session_user = db.session.get(User, session_user_id)
    return bool(session_user and session_user.is_admin)


@admin.route("/users/<int:id>/deactivate", methods=["POST"])
@admin.route("/users/<int:id>/deactivate/", methods=["POST"])
@token_auth.login_required(optional=True)  # type: ignore
def deactivate_user(id: int):
    """
    Deactivates a user account

    Deactivated users cannot take actions, and all their listings are deactivated
    """
    if not is_allowed_to_take_admin_action():
        return unauthorized("You do not have permission to perform this action")
    user = db.session.get(User, id)
    if user is None:
        return not_found("User not found")
    user.deactivate()
    user_listings = (
        db.session.execute(sa.select(Listing).where(Listing.userID == id))
        .scalars()
        .all()
    )
    for listing in user_listings:
        listing.deactivate()
        db.session.add(listing)
    db.session.add(user)
    db.session.commit()
    return user.to_dict()

@admin.route("/users/<username>/deactivate", methods=["POST"])
@admin.route("/users/<username>/deactivate/", methods=["POST"])
@token_auth.login_required(optional=True)  # type: ignore
def deactivate_user_by_username(username:str):
    """
    Deactivates a user account by username

    Deactivated users cannot take actions, and all their listings are deactivated
    """
    if not is_allowed_to_take_admin_action():
        return unauthorized("You do not have permission to perform this action")
    user = db.session.execute(sa.select(User).where(User.username == username)).scalar()
    if user is None:
        return not_found("User not found")
    user.deactivate()
    user_listings = (
        db.session.execute(sa.select(Listing).where(Listing.userID == user.id))
        .scalars()
        .all()
    )
    for listing in user_listings:
        listing.deactivate()
        db.session.add(listing)
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


@admin.route("/users/<int:id>/reactivate", methods=["POST"])
@admin.route("/users/<int:id>/reactivate/", methods=["POST"])
@token_auth.login_required(optional=True)  # type: ignore
def reactivate_user(id: int):
    """
    Reactivates the user account with id `id`

    Note that this does not reactivate the listings of the user
    """
    if not is_allowed_to_take_admin_action():
        return unauthorized("You do not have permission to perform this action")
    user = db.session.get(User, id)
    if user is None:
        return not_found("User not found")
    user.reactivate()
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


@admin.route("/users/<username>/reactivate", methods=["POST"])
@admin.route("/users/<username>/reactivate/", methods=["POST"])
@token_auth.login_required(optional=True)  # type: ignore
def reactivate_user_by_username(username:str):
    """
    Reactivates the user account with username `username`

    Note that this does not reactivate the listings of the user
    """
    if not is_allowed_to_take_admin_action():
        return unauthorized("You do not have permission to perform this action")
    user = db.session.execute(sa.select(User).where(User.username == username)).scalar()
    if user is None:
        return not_found("User not found")
    user.reactivate()
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


@admin.route("/users/<int:id>/make_admin", methods=["POST"])
@admin.route("/users/<int:id>/make_admin", methods=["POST"])
@token_auth.login_required(optional=True)  # type: ignore
def make_user_admin(id: int):
    """
    Grants the user with id `id` admin privileges
    """
    if not is_allowed_to_take_admin_action():
        return unauthorized("You do not have permission to perform this action")
    user = db.session.get(User, id)
    if user is None:
        return not_found("User not found")
    user.make_admin()
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


@admin.route("/users/new_admin", methods=["POST", "PUT"])
@admin.route("/users/new_admin/", methods=["POST", "PUT"])
@token_auth.login_required(optional=True)  # type: ignore
def create_user():
    """
    Creates a new user with admin privileges
    """
    if not is_allowed_to_take_admin_action():
        return unauthorized("You do not have permission to perform this action")

    data = request.get_json()
    if not all(name in data for name in ["username", "name", "email", "password"]):
        return bad_request('must include an username, a name, email and a password')
    data['email'] = data['email'].lower()
    if not User.valid_username(data['username']):
        return bad_request('Username does not meet requirements.\nUsername must only contain alpha-numeric characters.')
    if db.session.scalar(sa.select(User).where(
            User.username == data['username'])):
        return bad_request('Username already in use')
    if len(data["name"]) > 70 or len(data["name"]) < 1:
        return bad_request('Name does not meet requirements.\nName must be between 1 and 70 characters.')
    if not User.valid_email(data['email']):
        return bad_request('This is not a valid email address')
    if db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        return bad_request('Email address already in use')
    if not User.valid_password(data['password']):
        return bad_request('Password does not meet requirements\nPassword must be between 15 and 64 characters long.')
    user = User().from_dict(data, new_user=True).make_admin()
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201, {"Location": url_for("api.get_users", id=user.id)}


@admin.route("/listings/<int:id>/deactivate", methods=["POST"])
@admin.route("/listings/<int:id>/deactivate/", methods=["POST"])
@token_auth.login_required(optional=True)  # type: ignore
def deactivate_listing(id: int):
    """
    Deactivates a listing
    """
    if not is_allowed_to_take_admin_action():
        return unauthorized("You do not have permission to perform this action")
    listing = db.session.get(Listing, id)
    if listing is None:
        return not_found("Listing not found")
    listing.deactivate()
    db.session.add(listing)
    db.session.commit()
    return {"message": "Listing deactivated"}, 200


@admin.route("/listings/<int:id>/reactivate", methods=["POST"])
@admin.route("/listings/<int:id>/reactivate/", methods=["POST"])
@token_auth.login_required(optional=True)  # type: ignore
def reactivate_listing(id: int):
    """
    Reactivates a listing
    """
    if not is_allowed_to_take_admin_action():
        return unauthorized("You do not have permission to perform this action")
    listing = db.session.get(Listing, id)
    if listing is None:
        return not_found("Listing not found")
    listing.reactivate()
    db.session.add(listing)
    db.session.commit()
    return {"message": "Listing reactivated"}, 200
