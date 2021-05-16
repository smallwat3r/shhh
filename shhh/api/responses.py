from dataclasses import dataclass, field
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
class ReadResponse:
    """Read client response schema."""

    status: Status
    msg: str

    def make(self):
        """Make client response object."""
        return jsonify({"response": {"status": self.status.value, "msg": self.msg}})


@dataclass
class WriteResponse:
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

    def make(self):
        """Make client response object."""
        return jsonify(
            {
                "response": {
                    "status": self.status.value,
                    "details": self.details.value,
                    "slug": self.slug,
                    "link": self.link,
                    "expires_on": self.expires_on,
                }
            }
        )


@dataclass
class ErrorResponse:
    """Error client response schema."""

    details: str
    status: Status = Status.ERROR

    def make(self):
        """Make error response object."""
        return jsonify({"response": {"status": self.status.value, "details": self.details}})
