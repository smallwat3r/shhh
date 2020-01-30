#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : api.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 30.01.2020

"""Api tasks management."""
from datetime import datetime, timedelta, timezone

import html

from flask import request

from cryptography.fernet import InvalidToken

from . import database, logger, utils
from .encryption import Secret


def create_secret(passphrase, secret, expire):
    """Create a secret."""
    if not secret or secret == "":
        return {
            "status": "error",
            "details": "You need to enter a secret to encrypt.",
        }

    if len(secret) > 150:
        return {
            "status": "error",
            "details": "Your secret needs to have less than 150 characters.",
        }

    if not passphrase:
        return {
            "status": "error",
            "details": (
                "Please enter a passphrase. "
                "It needs minimun 5 characters, 1 number and 1 uppercase."
            ),
        }

    if not utils.passphrase_strength(passphrase):
        return {
            "status": "error",
            "details": (
                "The passphrase you used is too weak. "
                "It needs minimun 5 characters, 1 number and 1 uppercase."
            ),
        }

    if expire > 7:
        return {
            "status": "error",
            "details": "The maximum number of days to keep the secret alive is 7.",
        }

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    expires = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(days=expire)

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

    logger.info(f"{slug} created and expires on {expires}")
    timez = datetime.now(timezone.utc).astimezone().tzname()
    return {
        "status": "created",
        "details": "Secret successfully created.",
        "slug": slug,
        "link": f"{request.url_root}r/{slug}",
        "expires_on": f"{expires.strftime('%Y-%m-%d at %H:%M')} {timez}",
    }


def read_secret(slug, passphrase):
    """Read a secret."""
    if not passphrase:
        return {"status": "error", "msg": "Please enter a passphrase."}

    with database.DbConn() as db:
        encrypted = db.get("retrieve_from_slug.sql", {"slug_link": slug})

        if not encrypted:
            logger.warning(f"{slug} tried to read but do not exists in database")
            return {
                "status": "expired",
                "msg": "Sorry the data has expired or has already been read.",
            }

        try:
            msg = Secret(encrypted[0]["encrypted_text"], passphrase).decrypt()
        except InvalidToken:
            logger.warning(f"{slug} wrong passphrase used")
            return {"status": "error", "msg": "Sorry the passphrase is not valid."}

        # Automatically delete message from the database.
        db.commit("burn_message.sql", {"slug_link": slug})

    logger.info(f"{slug} was decrypted and deleted")
    return {"status": "success", "msg": html.escape(msg)}
