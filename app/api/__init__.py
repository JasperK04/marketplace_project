from flask import Blueprint

api = Blueprint("api", __name__)

from . import (  # noqa: E402,F401
	admin as admin,
	auth as auth,
	categories as categories,
	listings as listings,
	users as users,
)

__all__ = ["api", "admin", "auth", "categories", "listings", "users"]
