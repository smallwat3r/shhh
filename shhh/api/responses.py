from dataclasses import dataclass, field, fields
from enum import Enum
from urllib.parse import urljoin

from flask import current_app as app, jsonify, request, url_for


class Status(str, Enum):
    CREATED = "created"
    SUCCESS = "success"
    EXPIRED = "expired"
    INVALID = "invalid"
    ERROR = "error"


class Message(str, Enum):
    NOT_FOUND = ("Sorry, we can't find a secret, it has expired, been deleted "
                 "or has already been read.")
    EXCEEDED = ("The passphrase is not valid. You've exceeded the number of "
                "tries and the secret has been deleted.")
    INVALID = ("Sorry, the passphrase is not valid. Number of tries "
               "remaining: {remaining}")
    CREATED = "Secret successfully created."
    UNEXPECTED = "An unexpected error has occurred, please try again."


@dataclass
class BaseResponse:

    def make(self):
        return jsonify(
            {"response": {
                f.name: getattr(self, f.name)
                for f in fields(self)
            }})


@dataclass
class ReadResponse(BaseResponse):
    status: Status
    msg: str


@dataclass
class WriteResponse(BaseResponse):
    external_id: str
    expires_on: str
    link: str = field(init=False)
    status: Status = Status.CREATED
    details: Message = Message.CREATED

    def __post_init__(self):
        self.link = urljoin(request.url_root,
                            url_for("web.read", external_id=self.external_id))
        if host_config := app.config["SHHH_HOST"]:
            self.link = urljoin(
                host_config, url_for("web.read", external_id=self.external_id))


@dataclass
class ErrorResponse(BaseResponse):
    details: str
    status: Status = Status.ERROR
