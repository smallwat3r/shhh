from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from flask import Blueprint
from flask.views import MethodView
from webargs.flaskparser import parser, use_kwargs
from werkzeug.exceptions import HTTPException

from shhh.api.handlers import ErrorHandler, ReadHandler, WriteHandler
from shhh.api.schemas import ReadRequest, WriteRequest

if TYPE_CHECKING:
    from typing import NoReturn

    from flask import Response
    from marshmallow import ValidationError


@parser.error_handler
def handle_parsing_error(err: ValidationError, *args, **kwargs) -> NoReturn:
    raise HTTPException(ErrorHandler(err).make_response())


body = functools.partial(use_kwargs, location="json")
query = functools.partial(use_kwargs, location="query")


class Api(MethodView):

    @query(ReadRequest())
    def get(self, *args, **kwargs) -> Response:
        return ReadHandler(*args, **kwargs).make_response()

    @body(WriteRequest())
    def post(self, *args, **kwargs) -> Response:
        return WriteHandler(*args, **kwargs).make_response()


api = Blueprint("api", __name__, url_prefix="/api")
api.add_url_rule("/secret", view_func=Api.as_view("secret"))
