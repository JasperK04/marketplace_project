from flask import Blueprint, request, url_for
import sqlalchemy as sa
from app import db
from app.api import api
from app.api.auth import token_auth
from app.models.User import User
from app.models.Listing import Listing


admin = Blueprint("admin", __name__)
api.register_blueprint(admin, url_prefix='/admin')


@admin.route('/users/<int:id>/deactivate', methods=['POST'])
@token_auth.login_required
def deactivate_user(id):
    current_user = token_auth.current_user()
    print(current_user)
    if not current_user.is_admin:
        return {'error': 'You do not have permission to perform this action'}, 403

    user = db.get_or_404(User, id)
    user.deactivate()
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


@admin.route('/users/<int:id>/make_admin', methods=['POST'])
@admin.route('/users/<int:id>/make_admin', methods=['POST'])
@token_auth.login_required
def make_user_admin(id):
    current_user = token_auth.current_user()
    if not current_user.is_admin:
        return {'error': 'You do not have permission to perform this action'}, 403
    user = db.get_or_404(User, id)
    user.make_admin()
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


@admin.route('/users/new_admin', methods=['POST', 'PUT'])
@admin.route('/users/new_admin/', methods=['POST', 'PUT'])
@token_auth.login_required
def create_user():
    if not token_auth.current_user().is_admin:
        return {'error': 'You do not have permission to perform this action'}, 403

    data = request.get_json()
    if not all(name in data for name in ["name", "email", "password"]):
        return bad_request('must include a name, email and a password')
    data['email'] = data['email'].lower()
    if not User.valid_username(data['name']):
        return bad_request('Username does not meet requirements.\nUsername must only contain alpha-numeric characters.')
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
    return user.to_dict(), 201, {'Location': url_for('api.get_users',
                                                     id=user.id)}

@admin.route('/listings/<int:id>/deactivate', methods=['POST'])
@admin.route('/listings/<int:id>/deactivate/', methods=['POST'])
@token_auth.login_required
def deactivate_listing(id):
    current_user = token_auth.current_user()
    if not current_user.is_admin:
        return {'error': 'You do not have permission to perform this action'}, 403

    listing = db.get_or_404(Listing, id)
    listing.deactivate()
    db.session.add(listing)
    db.session.commit()
    return listing.to_dict()
