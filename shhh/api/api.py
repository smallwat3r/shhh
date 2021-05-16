# pylint: disable=no-self-use,too-many-arguments,unused-argument
import functools

from flask import Blueprint, Response, make_response
from flask.views import MethodView
from marshmallow import Schema, fields, validates_schema
from webargs.flaskparser import abort, parser, use_kwargs

from shhh.api.handlers import parse_error, read_secret, write_secret
from shhh.api.validators import Validator

api = Blueprint("api", __name__, url_prefix="/api")

json = functools.partial(use_kwargs, location="json")
query = functools.partial(use_kwargs, location="query")


class GetParams(Schema):
    """GET parameters."""

    slug = fields.Str(required=True, validate=Validator.slug)
    passphrase = fields.Str(required=True, validate=Validator.passphrase)


class PostParams(Schema):
    """POST parameters."""

    passphrase = fields.Str(
        required=True,
        validate=(Validator.passphrase, Validator.strength),
    )
    secret = fields.Str(required=True, validate=Validator.secret)
    days = fields.Int(validate=Validator.days)
    tries = fields.Int(validate=Validator.tries)
    haveibeenpwned = fields.Bool()

    @validates_schema
    def haveibeenpwned_checker(self, data, **kwargs):
        """Check the passphrase against haveibeenpwned if set to true."""
        if data.get("haveibeenpwned"):
            Validator.haveibeenpwned(data["passphrase"])


@parser.error_handler
def handle_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """Handle request parsing errors."""
    response, code = parse_error(err)
    return abort(response.make(), code)


class Api(MethodView):
    """API endpoint."""

    @query(GetParams())
    def get(self, slug: str, passphrase: str) -> Response:
        """Get secret request handler."""
        response, code = read_secret(slug, passphrase)
        return make_response(response.make(), code)

    @json(PostParams())
    def post(
        self,
        passphrase: str,
        secret: str,
        days: int = 3,
        tries: int = 5,
        haveibeenpwned: bool = False,
    ) -> Response:
        """Create secret request handler."""
        response, code = write_secret(passphrase, secret, days, tries, haveibeenpwned)
        return make_response(response.make(), code)


api.add_url_rule("/secret", view_func=Api.as_view("secret"))
