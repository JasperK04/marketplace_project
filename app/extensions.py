from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_session import Session
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth


db = SQLAlchemy()
migrate = Migrate()
session = Session()
login = LoginManager()
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
