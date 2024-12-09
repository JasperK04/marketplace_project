from . import api
from app import db
import sqlalchemy as sa
from flask import request
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