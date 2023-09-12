import functools
from http import HTTPStatus
from typing import NoReturn

from flask import Blueprint, Response, make_response
from flask.views import MethodView
from marshmallow import ValidationError
from webargs.flaskparser import abort, parser, use_kwargs

from shhh.api import handlers
from shhh.api.schemas import CallableResponse, ReadRequest, WriteRequest


def _handle(response: CallableResponse, code: HTTPStatus) -> Response:
    return make_response(response(), code)


@parser.error_handler
def handle_parsing_error(err: ValidationError, *args, **kwargs) -> NoReturn:
    abort(_handle(*handlers.parse_error(err)))


body = functools.partial(use_kwargs, location="json")
query = functools.partial(use_kwargs, location="query")


class Api(MethodView):

    @query(ReadRequest())
    def get(self, *args, **kwargs) -> Response:
        return _handle(*handlers.read(*args, **kwargs))

    @body(WriteRequest())
    def post(self, *args, **kwargs) -> Response:
        return _handle(*handlers.write(*args, **kwargs))


api = Blueprint("api", __name__, url_prefix="/api")
api.add_url_rule("/secret", view_func=Api.as_view("secret"))
