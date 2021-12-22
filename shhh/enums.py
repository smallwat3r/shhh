from enum import Enum, IntEnum


class LivenessClient(Enum):
    """Liveness client type."""

    WEB = "web"
    TASK = "task"


class ReadTriesValues(IntEnum):
    """Enum of allowed number of tries to read secrets."""

    THREE = 3
    FIVE = 5
    TEN = 10

    @classmethod
    def default(cls):  # pylint: disable=missing-function-docstring
        return cls.FIVE.value  # Needs .value as its being passed to Jinja


class SecretExpirationValues(Enum):
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


class EnvConfig(Enum):
    """Environment config values."""

    TESTING = "testing"
    DEV_LOCAL = "dev-local"
    DEV_DOCKER = "dev-docker"
    HEROKU = "heroku"
    PRODUCTION = "production"
