#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : api.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 13.01.2020
from datetime import datetime, timedelta, timezone

import html

from flask import jsonify, request
from cryptography.fernet import InvalidToken

from flask_restful import reqparse, Resource

from . import database, utils
from .encryption import Secret


class Create(Resource):
    """Create secret API."""

    def post(self):
        """Process POST request."""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument("secret", type=str, required=True)
        parser.add_argument("passphrase", type=str, required=True)
        parser.add_argument("days_expires", type=int, required=True)
        args = parser.parse_args()

        passphrase = args["passphrase"]
        secret = args["secret"]

        if not secret or secret == "":
            return jsonify(
                status="error", details="You need to enter a secret to encrypt."
            )

        if not utils.passphrase_strenght(passphrase):
            return jsonify(
                status="error",
                details=(
                    "The passphrase you used is too weak\n"
                    "It needs min 5 chars, 1 number and 1 uppercase."
                ),
            )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expires = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(
            days=int(args["days_expires"])
        )

        with database.DbConn() as db:
            slug = utils.generate_unique_slug(db)
            db.commit(
                "store_encrypt.sql",
                {
                    "slug_link": slug,
                    "encrypted_text": Secret(secret.encode(), passphrase).encrypt(),
                    "date_created": now,
                    "date_expires": expires,
                },
            )

        timez = datetime.now(timezone.utc).astimezone().tzname()
        return jsonify(
            status="created",
            link=f"{request.url_root}r/{slug}",
            expires_on=f"{expires.strftime('%Y-%m-%d at %H:%M')} {timez}",
        )


class Read(Resource):
    """Read secret API."""

    def get(self):
        """Process GET request."""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument("slug", type=str, required=True)
        parser.add_argument("passphrase", type=str, required=True)
        args = parser.parse_args()

        slug = args["slug"]
        passphrase = args["passphrase"]

        with database.DbConn() as db:
            encrypted = db.get("retrieve_from_slug.sql", {"slug_link": slug})

            if not encrypted:
                return jsonify(
                    status="expired",
                    msg="Sorry the data has expired \nor has already been read.",
                )

            try:
                msg = Secret(encrypted[0]["encrypted_text"], passphrase).decrypt()
            except InvalidToken:
                return jsonify(status="error", msg="Sorry the passphrase is not valid.")

            # Automatically delete message from the database.
            db.commit("burn_message.sql", {"slug_link": slug})

        return jsonify(status="success", msg=html.escape(msg))
