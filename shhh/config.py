#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : config.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Application config."""
import os

from . import ROOT_PATH


class DefaultConfig:
    """Default config values (dev-local)."""

    DEBUG = True
    DB_CREDENTIALS = {
        "host": os.getenv("HOST_MYSQL"),
        "user": os.getenv("USER_MYSQL"),
        "password": os.getenv("PASS_MYSQL"),
        "db": os.getenv("DB_MYSQL"),
    }

    CELERY_BROKER_URL = "redis://localhost:6379"
    CELERY_RESULT_BACKEND = "redis://localhost:6379"

    LOG_FILE = f"{ROOT_PATH}/logs/shhh.log"


class DockerConfig(DefaultConfig):
    """Docker development configuration (dev-docker)."""

    REDIS_PASS = os.getenv("REDIS_PASS")
    CELERY_BROKER_URL = f"redis://:{REDIS_PASS}@redis:6379"
    CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASS}@redis:6379"

    LOG_FILE = "/var/log/shhh/shhh.log"


class ProductionConfig(DefaultConfig):
    """Production configuration (production)."""
    # Note that this app is not yet designed to run in production

    DEBUG = False

    REDIS_PASS = os.getenv("REDIS_PASS")
    CELERY_BROKER_URL = f"redis://:{REDIS_PASS}@redis:6379"
    CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASS}@redis:6379"

    LOG_FILE = "/var/log/shhh/shhh.log"
