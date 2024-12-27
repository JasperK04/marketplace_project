from flask import render_template

from . import app, db
from .models.Listing import Listing


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    listings = db.session.query(Listing).filter_by(sold=False).all()
    return render_template("index.html", listings=listings)
