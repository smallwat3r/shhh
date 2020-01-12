#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : config.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Config."""
import os


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


class DockerConfig(DefaultConfig):
    """Docker development configuration (dev-docker)."""

    CELERY_BROKER_URL = "redis://redis:6379"
    CELERY_RESULT_BACKEND = "redis://redis:6379"


class ProductionConfig(DefaultConfig):
    """Production configuration (production)."""
    # Note that this app is not yet designed to run in production

    DEBUG = False

    CELERY_BROKER_URL = "redis://redis:6379"
    CELERY_RESULT_BACKEND = "redis://redis:6379"
