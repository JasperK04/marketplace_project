from . import api
from app import db
import sqlalchemy as sa
from flask import request, url_for
from app.api.errors import bad_request
from app.api.auth import token_auth

from app.models.User import User
from app.models.Listing import Listing
from app.models.Category import Category


@api.route('/listings/<int:id>', methods=['GET'])
def get_listing(id):
    return db.get_or_404(Listing, id).to_dict()

@api.route('/listings/', methods=['GET'])
@api.route('/listings', methods=['GET'])
def get_listings():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return Listing.to_collection_dict(sa.select(Listing), page, per_page,
                                   'api.get_listings')


@api.route('/listings/', methods=['POST'])
@api.route('/listings', methods=['POST'])
@token_auth.login_required
def create_listing():
    fields = ["title", "price", "description"]
    data = request.get_json()
    current_user: User = token_auth.current_user() #type: ignore
    data['userID'] = current_user.id

    if not (all(field in data for field in fields) and # check required fields
           ('category' in data ^ 'categoryID' in data)):  # category XOR categoryID
        return bad_request(f'must include: {", ".join(fields)} and category')

    if not db.session.scalar(sa.select(User).where( # check if the user exists
            User.id == data['userID'])):
        return bad_request('This user does not exist')

    if 'category' in data: # get categoryID from category name 
        if categoryID := db.session.scalar(sa.select(Category.id).where(
                Category.name == data['category'])):
            data['categoryID'] = categoryID
        else:
            return bad_request('This category does not exist')

    elif 'categoryID' in data and not db.session.scalar(sa.select(Category).where( # check if the category exists
            Category.id == data['categoryID'])):
        return bad_request('This category does not exist')
    
    listing = Listing() # create and commit new listing
    listing.from_dict(data)
    db.session.add(listing)
    db.session.commit()
    return listing.to_dict(), 201, {'Location': url_for('api.get_listing',
                                                     id=listing.id)}


@api.route('/listings/<int:id>', methods=['PATCH'])
@token_auth.login_required
def change_listing(id):
    data = request.get_json()
    current_user: User = token_auth.current_user() #type: ignore
    listing = db.get_or_404(Listing, id)
    
    if listing.userID != current_user.id: # check if the listing is made by the current user
        return bad_request('You cannot change listings of another user')

    if 'category' in data: # get categoryID from category name 
        if categoryID := db.session.scalar(sa.select(Category.id).where(
                Category.name == data['category'])):
            data['categoryID'] = categoryID
        else:
            return bad_request('This category does not exist')

    elif 'categoryID' in data and not db.session.scalar(sa.select(Category).where( # check if the category exists
            Category.id == data['categoryID'])):
        return bad_request('This category does not exist')
    
    listing.from_dict(data) # change and commit the listing
    db.session.add(listing)
    db.session.commit()
    return listing.to_dict(), 201, {'Location': url_for('api.get_listing',
                                                     id=listing.id)}


@api.route('/listings/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_listing(id):
    current_user: User = token_auth.current_user() #type: ignore
    listing = db.get_or_404(Listing, id)
    
    if listing.userID != current_user.id: # check if the listing is made by the current user
        return bad_request('You cannot change listings of another user')
    db.session.delete(listing)
    db.session.commit()
    return f"successfully deleted:\n{listing.to_dict()}"
