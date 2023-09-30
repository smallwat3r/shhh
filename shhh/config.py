import os
import logging

logger = logging.getLogger(__name__)


class DefaultConfig:
    """Default config values (dev-local)."""

    DEBUG = True

    # Postgres connection.
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "shhh")

    # SqlAlchemy
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

    #
    # Shhh optional custom configurations
    #

    # This variable can be used to specify a custom hostname to use as the
    # domain URL when Shhh creates a secret (ex: https://<domain-name.com>).
    # If not set, the hostname defaults to request.url_root, which should be
    # fine in most cases.
    SHHH_HOST = os.environ.get("SHHH_HOST")

    # Default max secret length
    try:
        SHHH_SECRET_MAX_LENGTH = int(
            os.environ.get("SHHH_SECRET_MAX_LENGTH", 250))
    except (ValueError, TypeError):
        SHHH_SECRET_MAX_LENGTH = 250
        logger.warning(
            "Provided value for SHHH_SECRET_MAX_LENGTH is not "
            "valid, using default value of %s",
            SHHH_SECRET_MAX_LENGTH)

    # Number of tries to reach the database before performing a read or write
    # operation. It could happens that the database is not reachable or is
    # asleep (for instance this happens often on Heroku free plans). The
    # default retry number is 5.
    try:
        SHHH_DB_LIVENESS_RETRY_COUNT = int(
            os.environ.get("SHHH_DB_LIVENESS_RETRY_COUNT", 5))
    except (ValueError, TypeError):
        SHHH_DB_LIVENESS_RETRY_COUNT = 5
        logger.warning(
            "Provided value for SHHH_DB_LIVENESS_RETRY_COUNT is not "
            "valid, using default value of %s",
            SHHH_DB_LIVENESS_RETRY_COUNT)

    # Sleep interval in seconds between database liveness retries. The default
    # value is 1 second.
    try:

        SHHH_DB_LIVENESS_SLEEP_INTERVAL = float(
            os.environ.get("SHHH_DB_LIVENESS_SLEEP_INTERVAL", 1))
    except (ValueError, TypeError):
        SHHH_DB_LIVENESS_SLEEP_INTERVAL = 1
        logger.warning(
            "Provided value for SHHH_DB_LIVENESS_SLEEP_INTERVAL is not "
            "valid, using default value of %s",
            SHHH_DB_LIVENESS_SLEEP_INTERVAL)


class TestConfig(DefaultConfig):
    """Testing configuration."""

    DEBUG = False
    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite://"

    SHHH_HOST = "http://test.test"
    SHHH_SECRET_MAX_LENGTH = 20
    SHHH_DB_LIVENESS_RETRY_COUNT = 1
    SHHH_DB_LIVENESS_SLEEP_INTERVAL = 0.1


class DevelopmentConfig(DefaultConfig):
    """Docker development configuration (dev-docker)."""

    SQLALCHEMY_ECHO = False


class HerokuConfig(DefaultConfig):
    """Heroku configuration (heroku)."""

    DEBUG = False
    SQLALCHEMY_ECHO = False

    # SQLAlchemy 1.4 removed the deprecated postgres dialect name, the name
    # postgresql must be used instead. This URL is automatically set on
    # Heroku, so change it from the code directly.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace(
        "postgres://", "postgresql://", 1)


class ProductionConfig(DefaultConfig):
    """Production configuration (production)."""

    DEBUG = False
    SQLALCHEMY_ECHO = False
