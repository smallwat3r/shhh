import enum
import functools

from flask import Blueprint
from flask_restful import Api, Resource
from marshmallow import Schema, fields
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
                            validate=(validators.passphrase,
                                      validators.strength))
    secret = fields.Str(required=True, validate=validators.secret)
    days = fields.Int(validate=validators.days)


class Create(Resource):
    """/api/c Create secret API."""

    @json(CreateParams())
    def post(self, passphrase, secret, days):
        """Post request handler."""
        response = create_secret(passphrase, secret, days)
        return {"response": response}


class ReadParams(Schema):
    """/api/r API parameters."""

    slug = fields.Str(required=True, validate=validators.slug)
    passphrase = fields.Str(required=True, validate=validators.passphrase)


class Read(Resource):
    """/api/r Read secret API."""

    @query(ReadParams())
    def get(self, slug, passphrase):
        """Get request handler."""
        response = read_secret(slug, passphrase)
        return {"response": response}


endpoint.add_resource(Create, "/c")
endpoint.add_resource(Read, "/r")
