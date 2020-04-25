from os import environ


class DefaultConfig:
    """Default config values (dev-local)."""

    DEBUG = True

    POSTGRE_HOST = environ.get("POSTGRE_HOST")
    POSTGRE_USER = environ.get("POSTGRE_USER")
    POSTGRE_PASSWORD = environ.get("POSTGRE_PASSWORD")
    POSTGRE_PORT = environ.get("POSTGRE_PORT", 5432)
    POSTGRE_DB = environ.get("POSTGRE_DB")

    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (f"postgresql+psycopg2://"
                               f"{POSTGRE_USER}:{POSTGRE_PASSWORD}"
                               f"@{POSTGRE_HOST}:{POSTGRE_PORT}"
                               f"/{POSTGRE_DB}")

    CELERY_BROKER_URL = "redis://localhost:6379"


class DockerConfig(DefaultConfig):
    """Docker development configuration (dev-docker)."""

    REDIS_PASS = environ.get("REDIS_PASS")
    CELERY_BROKER_URL = f"redis://:{REDIS_PASS}@redis:6379"

    SQLALCHEMY_ECHO = False


class ProductionConfig(DefaultConfig):
    """Production configuration (production)."""
    # Note that this app is not yet designed to run in production

    DEBUG = False

    REDIS_PASS = environ.get("REDIS_PASS")
    CELERY_BROKER_URL = f"redis://:{REDIS_PASS}@redis:6379"

    SQLALCHEMY_ECHO = False
