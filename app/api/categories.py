from . import api
from app import db
import sqlalchemy as sa
from flask import request, url_for
from app.api.errors import bad_request
from app.api.auth import token_auth

from app.models.Category import Category

@api.route('/category/<int:id>', methods=['GET'])
def get_category(id):
    return db.get_or_404(Category, id).to_dict()


@api.route('/category/', methods=['GET'])
@api.route('/category', methods=['GET'])
def get_categories():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return Category.to_collection_dict(sa.select(Category), page, per_page,
                                   'api.get_listings')


@api.route('/category/', methods=['POST', 'PUT'])
@api.route('/category', methods=['POST', 'PUT'])
@token_auth.login_required
def create_category():
    data = request.get_json()
    if "name" not in data: # check if category name is specified
        return bad_request('Must include a category name')
    if "description" not in data: # check if category description is specified
        return bad_request('Must include a category description')

    data['name'] = Category.normalize_name(data['name'])
    data['description'] = Category.normalize_description(data['description'])
    if not Category.valid_name(data['name']):
        return bad_request('This is not a valid category name')
    if db.session.scalar(sa.select(Category).where( # check the category name does not yet exist
            Category.name == data['name'])):
        return bad_request('This category already exists')

    cat = Category().from_dict(data) # create and commit new category
    db.session.add(cat)
    db.session.commit()
    return cat.to_dict(), 201, {'Location': url_for('api.get_category',
                                                     id=cat.id)}

# optional TODO: add authentication levels e.g. admin,
# such that only admins can change or delete categories

# @api.route('/category/<int:id>', methods=['PATCH'])
# @token_auth.login_required
# def change_category(id):
#     data = request.get_json()
#     cat = db.get_or_404(Category, id)
#     if "name" not in data: # check if category name is specified
#         return bad_request('can\'t change name if no name is specified')

#     if db.session.scalar(sa.select(Category).where( # check the category name does not yet exist
#             Category.name == data['name'])):
#         return bad_request('this category already exists')

#     cat.from_dict(data) # change and commit changes of the category
#     db.session.add(cat)
#     db.session.commit()
#     return cat.to_dict(), 201, {'Location': url_for('api.get_category',
#                                                      id=cat.id)}


# @api.route('/category/<int:id>', methods=['DELETE'])
# @token_auth.login_required
# def delete_category(id):
#     cat = db.get_or_404(Category, id)
#     db.session.delete(cat)
#     db.session.commit()
#     return f"successfully deleted:\n{cat.to_dict()}"
