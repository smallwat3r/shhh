#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : api_config.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 20.02.2020

"""Api configs."""
from enum import Enum, unique

from flask_restful import fields


HELP_CREATE = {
    "secret": "Secret message to encrypt.",
    "passphrase": "Passphrase to encrypt secret, min 5 chars, 1 number, 1 uppercase.",
    "days": "Number of days to keep alive (needs to be an integer).",
}

HELP_READ = {
    "slug": "Secret slug id.",
    "passphrase": "Passphrase shared to decrypt message.",
}

FIELDS_CREATE = {
    "status": fields.String,
    "details": fields.String,
    "slug": fields.String,
    "link": fields.String,
    "expires_on": fields.String,
}

FIELDS_READ = {
    "status": fields.String,
    "msg": fields.String,
}

@unique
class Status(Enum):
    """Api response status."""

    CREATED = "created"
    SUCCESS = "success"
    EXPIRED = "expired"
    ERROR = "error"


@unique
class ApiCreateArgs(Enum):
    """Create api arguments."""

    SECRET = "secret"
    PASSPHRASE = "passphrase"
    DAYS = "days"


@unique
class ApiReadArgs(Enum):
    """Read api arguments."""

    SLUG = "slug"
    PASSPHRASE = "passphrase"
