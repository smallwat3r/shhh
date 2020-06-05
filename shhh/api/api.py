# pylint: disable=no-self-use,too-many-arguments
import functools

from marshmallow import Schema, fields, validates_schema
from flask import Blueprint
from flask_restful import Api, Resource

from webargs.flaskparser import use_kwargs

from shhh.api import validators
from shhh.api.services import create_secret, read_secret

api = Blueprint("api", __name__)
endpoint = Api(api, prefix="/api")

json = functools.partial(use_kwargs, location="json")
query = functools.partial(use_kwargs, location="query")


class CreateParams(Schema):
    """/api/c API parameters."""

    passphrase = fields.Str(required=True,
                            validate=(validators.validate_passphrase,
                                      validators.validate_strength))
    secret = fields.Str(required=True, validate=validators.validate_secret)
    days = fields.Int(validate=validators.validate_days)
    tries = fields.Int(validate=validators.validate_tries)
    haveibeenpwned = fields.Bool()

    @validates_schema
    def haveibeenpwned_checker(self, data, **kwargs):
        """Check the passphrase against haveibeenpwned if set to true."""
        if data.get("haveibeenpwned"):
            validators.validate_haveibeenpwned(data["passphrase"])


class Create(Resource):
    """/api/c Create secret API."""
    @json(CreateParams())
    def post(self, passphrase, secret, days=3, tries=5, haveibeenpwned=False):
        """Post request handler."""
        response = create_secret(passphrase, secret, days, tries,
                                 haveibeenpwned)
        return {"response": response}


class ReadParams(Schema):
    """/api/r API parameters."""

    slug = fields.Str(required=True, validate=validators.validate_slug)
    passphrase = fields.Str(required=True,
                            validate=validators.validate_passphrase)


class Read(Resource):
    """/api/r Read secret API."""
    @query(ReadParams())
    def get(self, slug, passphrase):
        """Get request handler."""
        response = read_secret(slug, passphrase)
        return {"response": response}


endpoint.add_resource(Create, "/c")
endpoint.add_resource(Read, "/r")
