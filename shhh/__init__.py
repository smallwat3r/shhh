#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 14.01.2020

"""Init application."""
import os
import logging

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

# Logs config
# For security reasons do not log the user IP as this could compromise the data
# security for this app.
logging.basicConfig(
    filename=app.config["LOG_FILE"],
    level=logging.INFO,
    format='[%(asctime)s] [sev %(levelno)s] [%(levelname)s] [%(name)s]> %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S'
)
# Change default werkzeug logger to show only at WARNING level.
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logger = logging.getLogger("shhh")

# Api routes
from shhh.api import Create, Read

api_routes = Api(app, prefix="/api")
api_routes.add_resource(Create, "/c")
api_routes.add_resource(Read, "/r")

# Flask views
import shhh.views
