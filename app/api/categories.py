from . import api

@api.route("/categories")
def get_categories():
    pass

# TODO: Add more category stuff, e.g. category name from ID, ID's of all listings
# which belong to a category with a certain ID, (if you want to be really fancy,
# let the user specify what other info to retrieve for the listing