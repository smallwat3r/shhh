#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 14.01.2020

"""Init application."""
import os
import logging

from celery import Celery
from flask import Flask

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

# Application config
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
logging.basicConfig(
    filename=app.config["LOG_FILE"],
    level=logging.INFO,
    format="[%(asctime)s] [sev %(levelno)s] [%(levelname)s] [%(name)s]> %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
)
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logger = logging.getLogger("shhh")

# API Blueprint
from .api import _api

app.register_blueprint(_api)

# Flask views
import shhh.views
