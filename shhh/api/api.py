# pylint: disable=no-self-use,too-many-arguments
import functools

from flask import Blueprint, Response, make_response
from flask.views import MethodView
from marshmallow import Schema, fields, validates_schema
from webargs.flaskparser import use_kwargs

from shhh.api.handlers import read_secret, write_secret
from shhh.api.validators import Validator

api = Blueprint("api", __name__, url_prefix="/api")

json = functools.partial(use_kwargs, location="json")
query = functools.partial(use_kwargs, location="query")


class CreateParams(Schema):
    """/api/c API parameters."""

    passphrase = fields.Str(required=True, validate=(Validator.passphrase, Validator.strength),)
    secret = fields.Str(required=True, validate=Validator.secret)
    days = fields.Int(validate=Validator.days)
    tries = fields.Int(validate=Validator.tries)
    haveibeenpwned = fields.Bool()

    @validates_schema
    def haveibeenpwned_checker(self, data, **kwargs):
        """Check the passphrase against haveibeenpwned if set to true."""
        if data.get("haveibeenpwned"):
            Validator.haveibeenpwned(data["passphrase"])


class ReadParams(Schema):
    """/api/r API parameters."""

    slug = fields.Str(required=True, validate=Validator.slug)
    passphrase = fields.Str(required=True, validate=Validator.passphrase)


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
        response, code = write_secret(passphrase, secret, days, tries, haveibeenpwned)
        return make_response(response.make(), code)


class Read(MethodView):
    """/api/r Read secret API."""

    @query(ReadParams())
    def get(self, slug: str, passphrase: str) -> Response:
        """Get request handler."""
        response, code = read_secret(slug, passphrase)
        return make_response(response.make(), code)


api.add_url_rule("c", view_func=Create.as_view("create"))
api.add_url_rule("r", view_func=Read.as_view("read"))
