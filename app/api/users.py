from . import api
from app import db
import sqlalchemy as sa
from flask import request, url_for
from app.api.errors import bad_request
from app.models.User import User


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
    return user.to_dict(), 201, {'Location': url_for('api.get_user',
                                                     id=user.id)}

@api.route('/users/', methods=['POST'])
def create_user2():
    return create_user()