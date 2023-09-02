import re
import functools

from flask import Blueprint, Response, make_response
from flask import current_app as app
from flask.views import MethodView
from marshmallow import Schema, fields, pre_load, validate
from marshmallow import ValidationError
from webargs.flaskparser import abort, parser, use_kwargs

from shhh.api import handlers
from shhh.constants import (DEFAULT_EXPIRATION_TIME_VALUE,
                            DEFAULT_READ_TRIES_VALUE,
                            EXPIRATION_TIME_VALUES,
                            READ_TRIES_VALUES)

api = Blueprint("api", __name__, url_prefix="/api")

json = functools.partial(use_kwargs, location="json")
query = functools.partial(use_kwargs, location="query")


class _ReadSchema(Schema):
    external_id = fields.Str(required=True)
    passphrase = fields.Str(required=True)


def _passphrase_validator(passphrase: str) -> None:
    regex = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$")
    if regex.search(passphrase):
        return
    raise ValidationError(
        "Sorry, your passphrase is too weak. It needs minimum 8 characters, "
        "with 1 number and 1 uppercase.")


def _secret_validator(secret: str) -> None:
    max_length = app.config["SHHH_SECRET_MAX_LENGTH"]
    if len(secret) <= max_length:
        return
    raise ValidationError(
        f"The secret should not exceed {max_length} characters")


class _CreateSchema(Schema):
    passphrase = fields.Str(required=True, validate=_passphrase_validator)
    secret = fields.Str(required=True, validate=_secret_validator)
    expire = fields.Str(default=DEFAULT_EXPIRATION_TIME_VALUE,
                        validate=validate.OneOf(
                            EXPIRATION_TIME_VALUES.values()))
    tries = fields.Int(default=DEFAULT_READ_TRIES_VALUE,
                       validate=validate.OneOf(READ_TRIES_VALUES))

    @pre_load
    def secret_sanitise_newline(self, data: dict, **kwargs) -> dict[str, str]:
        if isinstance(data.get("secret"), str):
            data["secret"] = "\n".join(data["secret"].splitlines())
        return data


# pylint: disable=unused-argument
@parser.error_handler
def handle_parsing_error(err, req, schema, *, error_status_code,
                         error_headers):
    response, code = handlers.parse_error(err)
    return abort(response.make(), code)


class Api(MethodView):

    @query(_ReadSchema())
    def get(self, external_id: str, passphrase: str) -> Response:
        response, code = handlers.read_secret(external_id, passphrase)
        return make_response(response.make(), code)

    @json(_CreateSchema())
    def post(self,
             passphrase: str,
             secret: str,
             expire: str = DEFAULT_EXPIRATION_TIME_VALUE,
             tries: int = DEFAULT_READ_TRIES_VALUE) -> Response:
        response, code = handlers.write_secret(passphrase, secret,
                                               expire, tries)
        return make_response(response.make(), code)


api.add_url_rule("/secret", view_func=Api.as_view("secret"))
