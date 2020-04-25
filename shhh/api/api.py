import functools

from flask import Blueprint
from flask_restful import Api, Resource
from marshmallow import Schema, fields
from webargs.flaskparser import use_kwargs, parser, abort

from shhh.api.services import create_secret, read_secret

api = Blueprint("api", __name__)
endpoint = Api(api, prefix="/api")

body = functools.partial(use_kwargs, location="json")
query = functools.partial(use_kwargs, location="query")


class CreateParams(Schema):
    """/api/c API parameters."""

    passphrase = fields.Str(required=True)
    secret = fields.Str(required=True)
    days = fields.Int()


class ReadParams(Schema):
    """/api/r API parameters."""

    slug = fields.Str(required=True)
    passphrase = fields.Str(required=True)


@parser.error_handler
def handle_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """Handle request parsing errors."""
    abort(error_status_code, errors=err.messages)


# /api/c
class Create(Resource):
    """Create secret API."""

    @body(CreateParams())
    def post(self, passphrase, secret, days):
        """Post request handler."""
        response = create_secret(passphrase, secret, days)
        return {"response": response}


# /api/r
class Read(Resource):
    """Read secret API."""

    @query(ReadParams())
    def get(self, slug, passphrase):
        """Get request handler."""
        response = read_secret(slug, passphrase)
        return {"response": response}


endpoint.add_resource(Create, "/c")
endpoint.add_resource(Read, "/r")
