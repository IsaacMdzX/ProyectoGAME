import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _get_database_uri():
    return (
        os.environ.get("DATABASE_URL")
        or os.environ.get("SQLALCHEMY_DATABASE_URI")
        or f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )


def _get_engine_options(database_uri):
    if database_uri.startswith("postgres"):
        return {"connect_args": {"sslmode": "require"}}
    return {}


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key-for-dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MERCADOPAGO_ACCESS_TOKEN = os.environ.get("MERCADOPAGO_ACCESS_TOKEN")
    MERCADOPAGO_PUBLIC_KEY = os.environ.get("MERCADOPAGO_PUBLIC_KEY")


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = _get_engine_options(SQLALCHEMY_DATABASE_URI)


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = _get_engine_options(SQLALCHEMY_DATABASE_URI)
