#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 20.02.2020

"""Api blueprint."""
from flask import Blueprint
from flask_restful import Api

from .api import Create, Read

_api = Blueprint("_api", __name__)
api_routes = Api(_api, prefix="/api")

api_routes.add_resource(Create, "/c")
api_routes.add_resource(Read, "/r")
