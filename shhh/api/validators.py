# pylint: disable=unused-argument
import hashlib
import re
from typing import Union

import requests
from flask import current_app as app
from marshmallow import ValidationError

from shhh.config import ReadTriesValues, SecretExpirationValues


def pwned_password(passphrase: str) -> Union[int, bool]:
    """Check passphrase with Troy's Hunt haveibeenpwned API.

    Query the API to check if the passphrase has already been pwned in the
    past. If it has, returns the number of times it has been pwned, else
    returns False.

    Notes:
        (source haveibeenpwned.com)

        (...) implements a k-Anonymity model that allows a password to be
        searched for by partial hash. This allows the first 5 characters of a
        SHA-1 password hash (not case-sensitive) to be passed to the API.

        When a password hash with the same first 5 characters is found in the
        Pwned Passwords repository, the API will respond with an HTTP 200 and
        include the suffix of every hash beginning with the specified prefix,
        followed by a count of how many times it appears in the data set. The
        API consumer can then search the results of the response for the
        presence of their source hash.

    """
    # See nosec exclusion explanation in function docstring, we are cropping
    # the hash to use a k-Anonymity model to retrieve the pwned passwords.
    hasher = hashlib.sha1()  # nosec
    hasher.update(passphrase.encode("utf-8"))
    digest = hasher.hexdigest().upper()

    endpoint = "https://api.pwnedpasswords.com/range"
    r = requests.get(f"{endpoint}/{digest[:5]}", timeout=5)
    r.raise_for_status()

    for line in r.text.split("\n"):
        info = line.split(":")
        if info[0] == digest[5:]:
            return int(info[1])

    return False  # Password hasn't been pwned.


class Validator:
    """Validate API parameters."""

    @classmethod
    def strength(cls, passphrase: str) -> None:
        """Passphrase strength validation handler.

        Minimum 8 characters containing at least one number and one uppercase.

        """
        if passphrase:
            regex = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$")
            if not regex.search(passphrase) is not None:
                raise ValidationError(
                    "Passphrase too weak. Minimum 8 characters, including 1 number and 1 uppercase."
                )

    @classmethod
    def haveibeenpwned(cls, passphrase: str) -> None:
        """Validate passphrase against haveibeenpwned API."""
        try:
            times_pwned = pwned_password(passphrase)
        except Exception as err:  # pylint: disable=broad-except
            app.logger.error(err)
            times_pwned = False  # don't break if service isn't reachable.

        if times_pwned:
            raise ValidationError(
                f"This password has been pwned {times_pwned} time(s) "
                "(haveibeenpwned.com), please chose another one."
            )

    @classmethod
    def secret(cls, secret: str) -> None:
        """Secret validation handler."""
        if not secret:
            raise ValidationError("Missing a secret to encrypt.")
        if len(secret) > app.config["SHHH_SECRET_MAX_LENGTH"]:
            raise ValidationError(
                "The secret needs to have less than "
                f"{app.config['SHHH_SECRET_MAX_LENGTH']} characters."
            )

    @classmethod
    def passphrase(cls, passphrase: str) -> None:
        """Passphrase validation handler."""
        if not passphrase:
            raise ValidationError("Missing a passphrase.")

    @classmethod
    def slug(cls, slug: str) -> None:
        """Link validation handler."""
        if not slug:
            raise ValidationError("Missing a secret link.")

    @classmethod
    def expire(cls, expire: str) -> None:
        """Expire validation handler."""
        allowed = set(i.value for i in SecretExpirationValues)
        if not expire in allowed:
            raise ValidationError(f"The expiry value must be in: {allowed}")

    @classmethod
    def tries(cls, tries: str) -> None:
        """Tries validation handler."""
        allowed = set(i.value for i in ReadTriesValues)
        if not tries in allowed:
            raise ValidationError(f"The number of allowed tries must be in: {allowed}")
