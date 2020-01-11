#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Init application."""
import os

from flask import Flask

import redis

from celery import Celery
from celery.schedules import crontab

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)

# Load Flask configuration from Class.
configurations = {
    "development": "shhh.config.DefaultConfig",
    "production": "shhh.config.ProductionConfig",
}
app.config.from_object(configurations[os.getenv("FLASK_ENV")])

redis_db = redis.StrictRedis(
    host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], charset="utf-8", db=1
)

celery = Celery(
    app.name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"],
)

celery.conf.update(app.config)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute="*/5"), delete_expired_links.s())


@celery.task
def delete_expired_links():
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("old link deleted")

from shhh import views
