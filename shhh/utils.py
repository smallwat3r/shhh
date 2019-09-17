#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : utils.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Utils."""
import os
import string

from base64 import b64decode, b64encode

from passlib.hash import bcrypt

import pymysql
import secrets

from . import app
from simplecrypt import decrypt, encrypt


def generate_random_slug():
    """Generate random slug to access data."""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                   for _ in range(25))


def encrypt_message(passphrase, message):
    """Encrypt secret message."""
    cipher = encrypt(passphrase, message)
    return b64encode(cipher)


def decrypt_message(passphrase, encoded_data):
    """Decode encrypted secret message."""
    cipher = b64decode(encoded_data)
    return decrypt(passphrase, cipher).decode('utf-8')


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
