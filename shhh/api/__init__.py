from flask import Blueprint
from flask_restful import Api

from .api import Create, Read

_api = Blueprint("_api", __name__)
api_routes = Api(_api, prefix="/api")

api_routes.add_resource(Create, "/c")
api_routes.add_resource(Read, "/r")
