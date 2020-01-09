#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : config.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Config."""
import os


class DefaultConfig:
    """Default config values (Development)."""

    DEBUG = True
    DB_CREDENTIALS = {
        "host": os.getenv("HOST_MYSQL"),
        "user": os.getenv("USER_MYSQL"),
        "password": os.getenv("PASS_MYSQL"),
        "db": os.getenv("DB_MYSQL"),
    }


class ProductionConfig(DefaultConfig):
    """Production configuration."""

    DEBUG = False
