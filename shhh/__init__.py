#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Init application."""
import os

from flask import Flask

from celery import Celery

# import redis

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)

# Load Flask configuration from Class.
configurations = {
    "development": "shhh.config.DefaultConfig",
    "production": "shhh.config.ProductionConfig",
}
app.config.from_object(configurations[os.getenv("FLASK_ENV")])

celery = Celery(
    app.name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"],
)
# redis_db = redis.StrictRedis(
#     host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], charset="utf-8", db=1
# )
from shhh import views
