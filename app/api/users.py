from . import api
from app import db
import sqlalchemy as sa
from flask import request, url_for
from app.api.errors import bad_request
from app.models.User import User
from app.api.auth import token_auth


@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return db.get_or_404(User, id).to_dict()


@api.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(sa.select(User), page, per_page,
                                   'api.get_users')

@api.route('/users/', methods=['GET'])
def get_users2():
   return get_users()


@api.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not all(name in data for name in ["name", "email", "password"]):
        return bad_request('must include a name, email and a password')
    if db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        return bad_request('Email address already in use')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201, {'Location': url_for('api.get_users',
                                                     id=user.id)}

@api.route('/users/', methods=['POST'])
def create_user2():
    return create_user()


@api.route('/users', methods=['PUT'])
@token_auth.login_required
def update_user():
    new_password = False
    current_user: User = token_auth.current_user() # type: ignore
    id = current_user.id
    user = db.get_or_404(User, id)
    data = request.get_json()
    if 'name' in data and data['name'] != user.name and \
        db.session.scalar(sa.select(User).where(
            User.name == data['name'])):        
        return bad_request('please use a different name')
    if 'password' in data:
        if not user.check_password(data['password']):
            return bad_request('New password can not be the same as previous')
        new_password = True
    if 'email' in data:
        if data['email'] != user.email and \
            db.session.scalar(sa.select(User).where(
                User.email == data['email'])):
            return bad_request('please use a different email')
        elif db.session.scalar(sa.select(User).where(
                User.email == data['email'])):
            return bad_request('Email address already in use')
    user.from_dict(data, new_password)
    db.session.commit()
    return user.to_dict()

@api.route('/users/', methods=['PUT'])
@token_auth.login_required
def update_user2():
    return update_user()


@api.route('/users', methods=['DELETE'])
@token_auth.login_required
def delete_user():
    current_user: User = token_auth.current_user() # type: ignore
    id = current_user.id
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return f"successfully deleted:\n{user.to_dict()}"
    else:
        return bad_request('cannot delete a user that does not exist')