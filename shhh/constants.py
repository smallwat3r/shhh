from collections import OrderedDict
from enum import StrEnum

READ_TRIES_VALUES = (3, 5, 10)
DEFAULT_READ_TRIES_VALUE = 5

EXPIRATION_TIME_VALUES = OrderedDict([
    ("10 minutes", "10m"), ("30 minutes", "30m"), ("An hour", "1h"),
    ("3 hours", "3h"), ("6 hours", "6h"), ("A day", "1d"), ("2 days", "2d"),
    ("3 days", "3d"), ("5 days", "5d"), ("A week", "7d")
])
DEFAULT_EXPIRATION_TIME_VALUE = EXPIRATION_TIME_VALUES["3 days"]


class ClientType(StrEnum):
    WEB = "web"
    TASK = "task"


class EnvConfig(StrEnum):
    TESTING = "testing"
    DEV_LOCAL = "dev-local"
    DEV_DOCKER = "dev-docker"
    HEROKU = "heroku"
    PRODUCTION = "production"


class Status(StrEnum):
    CREATED = "created"
    SUCCESS = "success"
    EXPIRED = "expired"
    INVALID = "invalid"
    ERROR = "error"


class Message(StrEnum):
    NOT_FOUND = ("Sorry, we can't find a secret, it has expired, been deleted "
                 "or has already been read.")
    EXCEEDED = ("The passphrase is not valid. You've exceeded the number of "
                "tries and the secret has been deleted.")
    INVALID = ("Sorry, the passphrase is not valid. Number of tries "
               "remaining: {remaining}")
    CREATED = "Secret successfully created."
    UNEXPECTED = "An unexpected error has occurred, please try again."
