from . import api
from app import db
import sqlalchemy as sa
from flask import request, url_for
from app.api.errors import bad_request
from app.api.auth import token_auth

from app.models.User import User
from app.models.Listing import Listing
from app.models.Category import Category

@api.route('/category/<int:id>', methods=['GET'])
def get_category(id):
    return db.get_or_404(Category, id).to_dict()


@api.route('/category/', methods=['GET'])
@api.route('/category', methods=['GET'])
def get_categories():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return Listing.to_collection_dict(sa.select(Listing), page, per_page,
                                   'api.get_listings')


@api.route('/category/', methods=['POST'])
@api.route('/category', methods=['POST'])
@token_auth.login_required
def create_category():
    data = request.get_json()
    if "name" not in data:
        return bad_request('must include a category name')
    if db.session.scalar(sa.select(Category).where(
            Category.name == data['name'])):
        return bad_request('this category already exists')
    cat = Category()
    cat.from_dict(data)
    db.session.add(cat)
    db.session.commit()
    return cat.to_dict(), 201, {'Location': url_for('api.get_users',
                                                     id=cat.id)}

# TODO: Add more category stuff, e.g. category name from ID, ID's of all listings
# which belong to a category with a certain ID, (if you want to be really fancy,
# let the user specify what other info to retrieve for the listing
