from enum import Enum, unique


@unique
class Status(Enum):
    """Api response status."""

    CREATED = "created"
    SUCCESS = "success"
    EXPIRED = "expired"
    ERROR = "error"


@unique
class ApiCreateArgs(Enum):
    """Create api arguments."""

    SECRET = "secret"
    PASSPHRASE = "passphrase"
    DAYS = "days"


@unique
class ApiReadArgs(Enum):
    """Read api arguments."""

    SLUG = "slug"
    PASSPHRASE = "passphrase"
