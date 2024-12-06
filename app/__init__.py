from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path, getenv

basedir = path.abspath(path.dirname(__file__))

# Config stuff
# TODO: Organise this in a cleaner manner than just a bunch of Python code here

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv(
    "DB_URL"
) or "sqlite:///" + path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = getenv("TRACK_MODIFICATIONS") or False

app.config["SECRET_KEY"] = getenv("SECRET_KEY") or "secret-key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Imports to make the app work
from . import models, routes


# Create database
with app.app_context():
    db.create_all()