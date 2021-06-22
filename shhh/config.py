import enum
import os
from typing import Optional

from shhh.scheduler import delete_expired_links


class ReadTriesValues(enum.IntEnum):
    """Enum of allowed number of tries to read secrets."""

    THREE = 3
    FIVE = 5
    TEN = 10

    @classmethod
    def default(cls):  # pylint: disable=missing-function-docstring
        return cls.FIVE.value  # Needs .value as its being passed to Jinja


class SecretExpirationValues(enum.Enum):
    """Enum of allowed expiration values."""

    _10_MINUTES = "10m"
    _30_MINUTES = "30m"
    _AN_HOUR = "1h"
    _3_HOURS = "3h"
    _6_HOURS = "6h"
    _A_DAY = "1d"
    _2_DAYS = "2d"
    _3_DAYS = "3d"
    _5_DAYS = "5d"
    _A_WEEK = "7d"

    @classmethod
    def default(cls):  # pylint: disable=missing-function-docstring
        return cls._3_DAYS.value

    @classmethod
    def dict(cls) -> dict:
        """Return a dict of human friendly data."""
        return {i.name[1:].replace("_", " ").capitalize(): i.value for i in cls}


class EnvConfig(enum.Enum):
    """Environment config values."""

    TESTING = "testing"
    DEV_LOCAL = "dev-local"
    DEV_DOCKER = "dev-docker"
    HEROKU = "heroku"
    PRODUCTION = "production"


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
    SQLALCHEMY_DATABASE_URI: Optional[str] = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    #
    # Shhh specifics
    #

    # Scheduled jobs. Delete expired database records every 60 seconds.
    JOBS = [
        {
            "id": "delete_expired_links",
            "func": delete_expired_links,
            "trigger": "interval",
            "seconds": 60,
        }
    ]

    #
    # Shhh optional custom configurations
    #

    # This variable can be used to specify a custom hostname to use as the
    # domain URL when Shhh creates a secret (ex: https://<domain-name.com>). If not
    # set, the hostname defaults to request.url_root, which should be fine in
    # most cases.
    SHHH_HOST = os.environ.get("SHHH_HOST")

    # Default max secret length
    try:
        SHHH_SECRET_MAX_LENGTH = int(os.environ.get("SHHH_SECRET_MAX_LENGTH", 250))
    except (ValueError, TypeError):
        SHHH_SECRET_MAX_LENGTH = 250

    # Number of tries to reach the database before performing a read or write operation. It
    # could happens that the database is not reachable or is asleep (for instance this happens
    # often on Heroku free plans). The default retry number is 5.
    try:
        SHHH_DB_LIVENESS_RETRY_COUNT = int(os.environ.get("SHHH_DB_LIVENESS_RETRY_COUNT", 5))
    except (ValueError, TypeError):
        SHHH_DB_LIVENESS_RETRY_COUNT = 5

    # Sleep interval in seconds between database liveness retries. The default value is 1 second.
    try:
        SHHH_DB_LIVENESS_SLEEP_INTERVAL = float(
            os.environ.get("SHHH_DB_LIVENESS_SLEEP_INTERVAL", 1)
        )
    except (ValueError, TypeError):
        SHHH_DB_LIVENESS_SLEEP_INTERVAL = 1


class TestConfig(DefaultConfig):
    """Testing configuration."""

    DEBUG = False
    TESTING = True

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')}"
    )

    SHHH_HOST = "http://test.test"
    SHHH_DB_LIVENESS_RETRY_COUNT = 1
    SHHH_DB_LIVENESS_SLEEP_INTERVAL = 0.1


class DockerConfig(DefaultConfig):
    """Docker development configuration (dev-docker)."""

    SQLALCHEMY_ECHO = False


class HerokuConfig(DefaultConfig):
    """Heroku configuration (heroku)."""

    DEBUG = False
    SQLALCHEMY_ECHO = False

    # SQLAlchemy 1.4 removed the deprecated postgres dialect name, the name postgresql
    # must be used instead.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace(
        "postgres://", "postgresql://", 1
    )


class ProductionConfig(DefaultConfig):
    """Production configuration (production)."""

    DEBUG = False
    SQLALCHEMY_ECHO = False
