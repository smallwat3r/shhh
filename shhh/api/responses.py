from dataclasses import dataclass, field, fields
from enum import Enum

from flask import current_app as app
from flask import jsonify, request, url_for


class Status(Enum):
    """Body response statuses."""

    CREATED = "created"
    SUCCESS = "success"
    EXPIRED = "expired"
    INVALID = "invalid"
    ERROR = "error"


class Message(Enum):
    """Body response messages."""

    # fmt: off
    # pylint: disable=line-too-long
    NOT_FOUND = "Sorry, we can't find a secret, it has expired, been deleted or has already been read."
    EXCEEDED = "The passphrase is not valid. You've exceeded the number of tries and the secret has been deleted."
    INVALID = "Sorry the passphrase is not valid. Number of tries remaining: {remaining}."
    CREATED = "Secret successfully created."
    UNEXPECTED = "An unexpected error has occurred, please try again."
    # fmt: on


@dataclass
class BaseResponse:
    """Base Response dataclass."""

    def make(self):
        """Make a standard response from the dataclass fields."""
        return jsonify(
            {
                "response": {
                    f.name: getattr(self, f.name).value
                    if isinstance(getattr(self, f.name), Enum)
                    else getattr(self, f.name)
                    for f in fields(self)
                }
            }
        )


@dataclass
class ReadResponse(BaseResponse):
    """Read client response schema."""

    status: Status
    msg: str


@dataclass
class WriteResponse(BaseResponse):
    """Write client response schema."""

    slug: str
    expires_on: str
    link: str = field(init=False)
    status: Status = Status.CREATED
    details: Message = Message.CREATED

    def __post_init__(self):
        self.link = request.url_root.rstrip("/") + url_for("views.read", slug=self.slug)
        if _host := app.config["SHHH_HOST"]:
            self.link = _host.rstrip("/") + url_for("views.read", slug=self.slug)


@dataclass
class ErrorResponse(BaseResponse):
    """Error client response schema."""

    details: str
    status: Status = Status.ERROR
