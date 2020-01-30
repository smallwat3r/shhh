#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : api.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 13.01.2020

"""Api management."""
from flask_restful import reqparse, Resource, fields, marshal

from . import api_tasks

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


class Create(Resource):
    """Create secret API."""

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument(
            "secret", type=str, required=True, help=HELP_CREATE["secret"]
        )
        self.parser.add_argument(
            "passphrase", type=str, required=True, help=HELP_CREATE["passphrase"]
        )
        self.parser.add_argument(
            "days", type=int, required=True, help=HELP_CREATE["days"]
        )
        super().__init__()

    def post(self):
        """Process POST request to create secret."""
        args = self.parser.parse_args()
        response = api_tasks.create_secret(
            args["passphrase"], args["secret"], args["days"]
        )
        return {"response": marshal(response, FIELDS_CREATE)}


class Read(Resource):
    """Read secret API."""

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument(
            "slug", type=str, required=True, help=HELP_READ["slug"]
        )
        self.parser.add_argument(
            "passphrase", type=str, required=True, help=HELP_READ["passphrase"]
        )
        super().__init__()

    def get(self):
        """Process GET request to read secret."""
        args = self.parser.parse_args()
        response = api_tasks.read_secret(args["slug"], args["passphrase"])
        return {"response": marshal(response, FIELDS_READ)}
