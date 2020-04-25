from os import environ

from shhh.scheduler import delete_expired_links


class DefaultConfig:
    """Default config values (dev-local)."""

    DEBUG = True

    # Scheduled jobs.
    JOBS = [{
        "id": "delete_expired_links",
        "func": delete_expired_links,
        "trigger": "interval",
        "seconds": 60
    }]

    # Postgres connection.
    POSTGRES_HOST = environ.get("POSTGRES_HOST")
    POSTGRES_USER = environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")
    POSTGRES_PORT = environ.get("POSTGRES_PORT", 5432)
    POSTGRES_DB = environ.get("POSTGRES_DB")

    # SqlAlchemy
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (f"postgresql+psycopg2://"
                               f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
                               f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
                               f"/{POSTGRES_DB}")


class DockerConfig(DefaultConfig):
    """Docker development configuration (dev-docker)."""

    SQLALCHEMY_ECHO = False


class ProductionConfig(DefaultConfig):
    """Production configuration (production)."""

    DEBUG = False
    SQLALCHEMY_ECHO = False
