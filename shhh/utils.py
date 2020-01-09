#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : utils.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Utils."""
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta

import html

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import secrets

from . import database, ROOT_PATH


def _generate_random_slug():
    """Generate random slug to access data.
    This slug ID will be used by the recipient to read the
    secret.
    """
    return secrets.token_urlsafe(15)


def __derive_key(passphrase, salt, iterations=100_000):
    """Derive a secret key from a given passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend(),
    )
    return urlsafe_b64encode(kdf.derive(passphrase))


def _encrypt_message(message, passphrase, iterations=100_000):
    """Encrypt secret with passphrase."""
    salt = secrets.token_bytes(16)
    key = __derive_key(passphrase.encode(), salt, iterations)
    return urlsafe_b64encode(
        b"%b%b%b"
        % (
            salt,
            iterations.to_bytes(4, "big"),
            urlsafe_b64decode(Fernet(key).encrypt(message)),
        )
    )


def _decrypt_message(crypted_data, passphrase):
    """Decrypt secret with passphrase."""
    decoded = urlsafe_b64decode(crypted_data)
    salt, iter, crypted_data = (
        decoded[:16],
        decoded[16:20],
        urlsafe_b64encode(decoded[20:]),
    )
    iterations = int.from_bytes(iter, "big")
    key = __derive_key(passphrase.encode(), salt, iterations)
    return Fernet(key).decrypt(crypted_data).decode("utf-8")


def generate_link(secret, passphrase, expires):
    """Generate link to access secret."""
    link = _generate_random_slug()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with database.DbConn(ROOT_PATH) as db:
        db.commit(
            "store_encrypt.sql",
            {
                "slug_link": link,
                "encrypted_text": _encrypt_message(secret.encode(), passphrase),
                "date_created": now,
                "date_expires": (
                    datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
                    + timedelta(days=int(expires))
                ),
            },
        )
    return link


def decrypt(slug, passphrase):
    """Decrypt message from slug."""
    with database.DbConn(ROOT_PATH) as db:
        encrypted = db.get("retrieve_from_slug.sql", {"slug": slug})

    if not encrypted:
        return {"status": "expired", "msg": "Sorry the data has expired."}

    try:
        msg = html.escape(_decrypt_message(encrypted[0]["encrypted_text"], passphrase))

    except InvalidToken:
        return {"status": "error", "msg": "Sorry the passphrase is not valid."}

    return {"status": "success", "msg": msg}
