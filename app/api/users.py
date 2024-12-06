from . import api


@api.route("/users")
def get_users():
    pass

# TODO: Add more user stuff, e.g. user by id,
#  edit user profile if logged in as that user, etc