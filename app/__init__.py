from os import getenv

from flask import Flask
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from app.api import api
from app.cli import cli
from app.config import config
from app.errors import register_error_handler
from app.extensions import db, login, migrate, session
from app.logging import setup_logging
from app.routes import routes


def create_app() -> Flask:
    app = Flask(__name__)
    environment = getenv("FLASK_ENV", "development")
    app.config.from_object(config[environment])

    register_extensions(app)
    register_blueprints(app)
    register_error_handler(app)

    create_db(app)

    if environment == "production":
        setup_logging()

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    session.init_app(app)
    login.init_app(app)
    login.login_view = "routes.login"  # type: ignore[assignment]


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(routes)
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(cli)


def create_db(app: Flask) -> None:
    if getenv("FLASK_ENV", "development") != "development":
        return

    with app.app_context():
        inspector = inspect(db.engine)
        if inspector.get_table_names():
            return

        try:
            db.create_all()
        except OperationalError as exc:
            if "already exists" not in str(exc).lower():
                raise
