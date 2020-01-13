#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Init application."""
import os

from flask import Flask

from celery import Celery
from flask_restful import Api

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# Global config
configurations = {
    "dev-local": "shhh.config.DefaultConfig",
    "dev-docker": "shhh.config.DockerConfig",
    "production": "shhh.config.ProductionConfig",
}
app.config.from_object(configurations[os.getenv("FLASK_ENV")])

# Celery config
celery = Celery(
    app.name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"],
)

# Api routes
from shhh.api import Create, Read

api_routes = Api(app, prefix="/api")
api_routes.add_resource(Create, '/c')
api_routes.add_resource(Read, '/r')

# Flask views
import shhh.views
