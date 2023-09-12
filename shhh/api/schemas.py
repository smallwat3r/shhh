import re
from dataclasses import dataclass, field, fields as dfields
from urllib.parse import urljoin

from flask import Response, current_app as app, jsonify, request, url_for
from marshmallow import Schema, ValidationError, fields, pre_load, validate

from shhh.constants import (DEFAULT_EXPIRATION_TIME_VALUE,
                            DEFAULT_READ_TRIES_VALUE,
                            EXPIRATION_TIME_VALUES,
                            READ_TRIES_VALUES,
                            Message,
                            Status)


class ReadRequest(Schema):
    """Schema for inbound read requests."""
    external_id = fields.Str(required=True)
    passphrase = fields.Str(required=True)


def _passphrase_validator(passphrase: str) -> None:
    regex = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$")
    if not regex.search(passphrase):
        raise ValidationError("Sorry, your passphrase is too weak. It needs "
                              "minimum 8 characters, with 1 number and 1 "
                              "uppercase.")


def _secret_validator(secret: str) -> None:
    max_length = app.config["SHHH_SECRET_MAX_LENGTH"]
    if len(secret) > max_length:
        raise ValidationError(f"The secret should not exceed {max_length} "
                              "characters.")


class WriteRequest(Schema):
    """Schema for inbound write requests."""
    passphrase = fields.Str(required=True, validate=_passphrase_validator)
    secret = fields.Str(required=True, validate=_secret_validator)
    expire = fields.Str(load_default=DEFAULT_EXPIRATION_TIME_VALUE,
                        validate=validate.OneOf(
                            EXPIRATION_TIME_VALUES.values()))
    tries = fields.Int(load_default=DEFAULT_READ_TRIES_VALUE,
                       validate=validate.OneOf(READ_TRIES_VALUES))

    @pre_load
    def secret_sanitise_newline(self, data, **kwargs):
        if isinstance(data.get("secret"), str):
            data["secret"] = "\n".join(data["secret"].splitlines())
        return data


@dataclass
class CallableResponse:

    def __call__(self) -> Response:
        return jsonify({
            "response": {
                f.name: getattr(self, f.name)
                for f in dfields(self)
            }
        })


@dataclass
class ReadResponse(CallableResponse):
    """Schema for outbound read responses."""
    status: Status
    msg: str


@dataclass
class WriteResponse(CallableResponse):
    """Schema for outbound write responses."""
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
class ErrorResponse(CallableResponse):
    """Schema for outbound error responses."""
    details: str
    status: Status = Status.ERROR
