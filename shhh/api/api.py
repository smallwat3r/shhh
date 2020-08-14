# pylint: disable=no-self-use,too-many-arguments
import functools

from flask import Blueprint, Response, jsonify, make_response
from flask.views import MethodView
from marshmallow import Schema, fields, validates_schema
from webargs.flaskparser import use_kwargs

from shhh.api import validators
from shhh.api.utils import create_secret, read_secret

api = Blueprint("api", __name__, url_prefix="/api")

json = functools.partial(use_kwargs, location="json")
query = functools.partial(use_kwargs, location="query")


class CreateParams(Schema):
    """/api/c API parameters."""

    passphrase = fields.Str(
        required=True,
        validate=(validators.validate_passphrase, validators.validate_strength),
    )
    secret = fields.Str(required=True, validate=validators.validate_secret)
    days = fields.Int(validate=validators.validate_days)
    tries = fields.Int(validate=validators.validate_tries)
    haveibeenpwned = fields.Bool()

    @validates_schema
    def haveibeenpwned_checker(self, data, **kwargs):
        """Check the passphrase against haveibeenpwned if set to true."""
        if data.get("haveibeenpwned"):
            validators.validate_haveibeenpwned(data["passphrase"])


class Create(MethodView):
    """/api/c Create secret API."""

    @json(CreateParams())
    def post(
        self,
        passphrase: str,
        secret: str,
        days: int = 3,
        tries: int = 5,
        haveibeenpwned: bool = False,
    ) -> Response:
        """Post request handler."""
        response, code = create_secret(passphrase, secret, days, tries, haveibeenpwned)
        return make_response(jsonify({"response": response}), code)


class ReadParams(Schema):
    """/api/r API parameters."""

    slug = fields.Str(required=True, validate=validators.validate_slug)
    passphrase = fields.Str(required=True, validate=validators.validate_passphrase)


class Read(MethodView):
    """/api/r Read secret API."""

    @query(ReadParams())
    def get(self, slug: str, passphrase: str) -> Response:
        """Get request handler."""
        response, code = read_secret(slug, passphrase)
        return make_response(jsonify({"response": response}), code)


api.add_url_rule("c", view_func=Create.as_view("create"))
api.add_url_rule("r", view_func=Read.as_view("read"))
