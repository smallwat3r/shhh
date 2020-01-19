#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : encryption.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 13.01.2020

"""Encryption management."""
import secrets

from base64 import urlsafe_b64decode, urlsafe_b64encode

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Secret:
    """Secrets encryption / decryption management."""

    def __init__(self, secret, passphrase):
        self.secret = secret
        self.passphrase = passphrase

    def __derive_key(self, salt, iterations):
        """Derive a secret key from a given passphrase and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return urlsafe_b64encode(kdf.derive(self.passphrase.encode()))

    def encrypt(self, iterations=100_000):
        """Encrypt secret."""
        salt = secrets.token_bytes(16)
        key = self.__derive_key(salt, iterations)
        return urlsafe_b64encode(
            b"%b%b%b"
            % (
                salt,
                iterations.to_bytes(4, "big"),
                urlsafe_b64decode(Fernet(key).encrypt(self.secret)),
            )
        )

    def decrypt(self):
        """Decrypt secret."""
        decoded = urlsafe_b64decode(self.secret)
        salt, iter, message = (
            decoded[:16],
            decoded[16:20],
            urlsafe_b64encode(decoded[20:]),
        )
        iterations = int.from_bytes(iter, "big")
        key = self.__derive_key(salt, iterations)
        return Fernet(key).decrypt(message).decode("utf-8")
