#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : utils.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

'''Utils.'''
from base64 import urlsafe_b64decode as b64d, urlsafe_b64encode as b64e
from datetime import datetime, timedelta

import html

from passlib.hash import bcrypt

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import secrets

from . import database, ROOT_PATH


def _generate_random_slug():
    '''Generate random slug to access data.
    This slug ID will be used by the recipient to read the
    secret.
    '''
    return secrets.token_urlsafe(15)


def __derive_key(passphrase, salt, iterations=100_000):
    '''Derive a secret key from a given passphrase and salt.'''
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=default_backend()
    )
    return b64e(kdf.derive(passphrase))


def _encrypt_message(message, passphrase, iterations=100_000):
    '''Encrypt secret with passphrase.'''
    salt = secrets.token_bytes(16)
    key = __derive_key(passphrase.encode(), salt, iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )


def _decrypt_message(crypted_data, passphrase):
    '''Decrypt secret with passphrase.'''
    decoded = b64d(crypted_data)
    salt, iter, crypted_data = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = __derive_key(passphrase.encode(), salt, iterations)
    return Fernet(key).decrypt(crypted_data).decode('utf-8')


def _encrypt_passphrase(passphrase):
    '''Encrypt passphrase to open message.'''
    return bcrypt.encrypt(passphrase)


def _validate_passphrase(passphrase, hashed):
    '''Validate passphrase to open message.'''
    return bcrypt.verify(passphrase, hashed)


def generate_link(secret, passphrase, expires):
    '''Generate link to access secret.'''
    link = _generate_random_slug()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with database.DbConn(ROOT_PATH) as db:
        db.commit('store_encrypt.sql', {
            'slug_link': link,
            'passphrase': _encrypt_passphrase(passphrase),
            'encrypted_text': _encrypt_message(secret.encode(), passphrase),
            'date_created': now,
            'date_expires': (datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                             + timedelta(days=int(expires)))
        })
    return {'slug': link, 'expires': expires}


def decrypt(slug, passphrase):
    '''Decrypt message from slug.'''
    with database.DbConn(ROOT_PATH) as db:
        encrypted = db.get('retrieve_from_slug.sql', {'slug': slug})

    if not encrypted:
        return {'status': 'error', 'msg': 'Sorry the data has expired'}

    if not _validate_passphrase(passphrase, encrypted[0]['passphrase']):
        return {'status': 'error', 'msg': 'Sorry the passphrase is not valid'}

    msg = html.escape(
        _decrypt_message(encrypted[0]['encrypted_text'], passphrase)
    )
    return {'status': 'success', 'msg': '<br />'.join(msg.split('\n'))}
