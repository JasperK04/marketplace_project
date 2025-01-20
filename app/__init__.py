from flask import Flask
from os import getenv

from app.extensions import db, migrate, session, login
from app.config import config
from app.routes import routes
from app.api import api
from app.cli import cli
from app.errors import register_error_handler
from app.logging import setup_logging


def create_app() -> Flask:
    app = Flask(__name__)
    enviroment = getenv("FLASK_ENV", "development")
    app.config.from_object(config[enviroment])

    register_extensions(app)
    register_blueprints(app)
    register_error_handler(app)

    create_db(app)

    if enviroment == "production":
        setup_logging()

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    session.init_app(app)
    login.init_app(app)
    login.login_view = "routes.login"


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(routes)
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(cli)


def create_db(app: Flask) -> None:
    with app.app_context():
        db.create_all()
