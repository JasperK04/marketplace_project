from . import api


@api.route("/listings", methods=["GET"])
def get_listings():
    pass

# TODO: Add more Listing stuff, e.g. listing by id, by price above/below something,
#  edit listings if logged in as the user who created them,
#  create new listings if logged in, etc
