import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DB_PATH = os.path.join(BASE_DIR, "data", "marketplace.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    PICTURE_FOLDER = os.path.abspath("app/static/assets/images/user_uploaded")
    FALLBACK_DB_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", FALLBACK_DB_URI)


class DevelopmentConfig(Config):
    """Development configuration"""

    SECRET_KEY = "secret-key"


class ProductionConfig(Config):
    """Production configuration"""

    if os.environ.get("SECRET_KEY") is None:
        raise ValueError(
            "SECRET_KEY must be set as an environment variable in production"
        )
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if os.environ.get("UPLOAD_FOLDER") is not None:
        UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")
    if os.environ.get("RESIZED_FOLDER") is not None:
        RESIZED_FOLDER = os.environ.get("RESIZED_FOLDER")


config: dict[str, type[DevelopmentConfig] | type[ProductionConfig]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
