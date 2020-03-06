#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : task_read.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 20.02.2020

"""Api task task to read a secret."""
import html

from cryptography.fernet import InvalidToken

from ..config.api_config import Status
from ... import logger
from ...utils import database
from ...utils.encryption import Secret


def read_secret(slug, passphrase):
    """Read a secret."""
    if not passphrase:
        return {"status": Status.ERROR.value, "msg": "Please enter a passphrase."}

    with database.DbConn() as db:
        encrypted = db.get("retrieve_from_slug.sql", {"slug_link": slug})

        if not encrypted:
            logger.warning(f"{slug} tried to read but do not exists in database")
            return {
                "status": Status.EXPIRED.value,
                "msg": "Sorry the data has expired or has already been read.",
            }

        try:
            msg = Secret(encrypted[0]["encrypted_text"], passphrase).decrypt()
        except InvalidToken:
            logger.warning(f"{slug} wrong passphrase used")
            return {
                "status": Status.ERROR.value,
                "msg": "Sorry the passphrase is not valid.",
            }

        # Automatically delete message from the database.
        db.commit("burn_message.sql", {"slug_link": slug})

    logger.info(f"{slug} was decrypted and deleted")
    return {"status": Status.SUCCESS.value, "msg": html.escape(msg)}
