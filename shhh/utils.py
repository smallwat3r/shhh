#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : utils.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Utils."""
import os
import string

from base64 import urlsafe_b64decode as b64d, urlsafe_b64encode as b64e

from passlib.hash import bcrypt

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import pymysql
import secrets

from . import app


def generate_random_slug():
    """Generate random slug to access data."""
    return secrets.token_urlsafe()


def _derive_key(passphrase, salt, iterations=100_000):
    """Derive a secret key from a given passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=default_backend()
    )
    return b64e(kdf.derive(passphrase))


def encrypt_message(message, passphrase, iterations=100_000):
    """Encrypt secret with passphrase."""
    salt = secrets.token_bytes(16)
    key = _derive_key(passphrase.encode(), salt, iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )


def decrypt_message(crypted_data, passphrase):
    """Decrypt secret with passphrase."""
    decoded = b64d(crypted_data)
    salt, iter, crypted_data = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = _derive_key(passphrase.encode(), salt, iterations)
    return Fernet(key).decrypt(crypted_data).decode('utf-8')


def encrypt_passphrase(passphrase):
    """Encrypt passphrase to open message."""
    return bcrypt.encrypt(passphrase)


def validate_passphrase(passphrase, hashed):
    """Validate passphrase to open message."""
    return bcrypt.verify(passphrase, hashed)


class DbConn:
    """Manage Database connection and user actions.

    We are loading our SQL requests from raw files located inside each
    module directories under a SQL folder.
    """

    __slots__ = ('cnx', 'cur', 'path_temp')

    def __init__(self, path_temp):
        """Make connection to MySql DB."""
        self.cnx = pymysql.connect(charset="utf8",
                                   **app.config['DB_CREDENTIALS'])
        self.cur = self.cnx.cursor()
        self.path_temp = os.path.join(path_temp, 'sql')

    def __enter__(self):
        """Load context manager."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Close DB connection."""
        self.cur.close()

    def close(self):
        """Close DB connection."""
        self.cur.close()

    @staticmethod
    def _render_template(filepath):
        """Return SQL content from file."""
        with open(filepath) as f:
            return f.read()

    def get(self, query, args={}):
        """Return SQL results in a dict format."""

        def _return_null_format_by_type(value):
            """Return correct value from value type."""
            if type(value).__name__ == 'int':
                return 0

            elif type(value).__name__ == 'float':
                return 0.0

            return ''

        self.cur.execute(
            self._render_template(os.path.join(self.path_temp, query)),
            args
        )
        r = [
            dict((self.cur.description[i][0], value if value
                  else _return_null_format_by_type(value))
                 for i, value in enumerate(row))
            for row in self.cur.fetchall()
        ]
        return r if r else None

    def commit(self, query, args={}):
        """Commit SQL request."""
        self.cur.execute(self._render_template(
            os.path.join(self.path_temp, query)), args)
        self.cnx.commit()
