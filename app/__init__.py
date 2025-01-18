from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_session import Session
from os import path, getenv

basedir = path.abspath(path.dirname(__file__))

# Config stuff
# TODO: Organise this in a cleaner manner than just a bunch of Python code here

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv(
    "DB_URL"
) or "sqlite:///" + path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = getenv("TRACK_MODIFICATIONS") or False
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SECRET_KEY"] = getenv("SECRET_KEY") or "secret-key"
app.config['UPLOAD_FOLDER'] = path.abspath('app/static/assets/images/user_uploaded/listings/')
app.config['RESIZED_FOLDER'] = path.abspath('app/static/assets/images/user_uploaded/listings_resized/')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
session = Session(app)

login = LoginManager(app)
login.login_view = 'login'

# Imports to make the app work
from . import models, routes, api, cli

app.register_blueprint(api.api, url_prefix='/api')
app.register_blueprint(cli.cli)

# Create database
with app.app_context():
    db.create_all()
