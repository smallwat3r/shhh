import html
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Dict, Tuple

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app as app
from flask import request

from shhh.api.validators import Status
from shhh.models import Entries


class Secret:
    """Secrets encryption / decryption management."""

    __slots__ = ("secret", "passphrase")

    def __init__(self, secret: bytes, passphrase: str):
        self.secret = secret
        self.passphrase = passphrase

    def __derive_key(self, salt: bytes, iterations: int) -> bytes:
        """Derive a secret key from a given passphrase and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return urlsafe_b64encode(kdf.derive(self.passphrase.encode()))

    def encrypt(self, iterations: int = 100_000) -> bytes:
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

    def decrypt(self) -> str:
        """Decrypt secret."""
        decoded = urlsafe_b64decode(self.secret)
        salt, iteration, message = (
            decoded[:16],
            decoded[16:20],
            urlsafe_b64encode(decoded[20:]),
        )
        iterations = int.from_bytes(iteration, "big")
        key = self.__derive_key(salt, iterations)
        return Fernet(key).decrypt(message).decode("utf-8")


def read_secret(slug: str, passphrase: str) -> Tuple[Dict, int]:
    """Read a secret.

    Args:
        slug (str): Unique slug link to access the secret.
        passphrase (str): Passphrase needed to decrypt the secret.

    """
    secret = Entries.query.filter_by(slug_link=slug).first()
    if not secret:
        app.logger.warning(f"{slug} tried to read but do not exists in database")
        response = {
            "status": Status.EXPIRED.value,
            "msg": (
                "Sorry, we can't find a secret, it has expired, "
                "been deleted or has already been read."
            ),
        }
        return (response, HTTPStatus.NOT_FOUND.value)

    try:
        msg = Secret(secret.encrypted_text, passphrase).decrypt()
    except InvalidToken:
        remaining = secret.tries - 1
        if remaining == 0:
            # Number of tries exceeded, delete secret
            app.logger.warning(f"{slug} tries to open secret exceeded")
            secret.delete()
            response = {
                "status": Status.INVALID.value,
                "msg": (
                    "The passphrase is not valid. You've exceeded the "
                    "number of tries and the secret has been deleted."
                ),
            }
            return (response, HTTPStatus.UNAUTHORIZED.value)

        secret.update(tries=remaining)
        app.logger.warning(
            f"{slug} wrong passphrase used. Number of tries remaining: {remaining}"
        )
        response = {
            "status": Status.INVALID.value,
            "msg": (
                "Sorry the passphrase is not valid. "
                f"Number of tries remaining: {remaining}"
            ),
        }
        return (response, HTTPStatus.UNAUTHORIZED.value)

    secret.delete()  # Delete message after it's read
    app.logger.info(f"{slug} was decrypted and deleted")
    response = {"status": Status.SUCCESS.value, "msg": html.escape(msg)}
    return (response, HTTPStatus.OK.value)


def _generate_unique_slug() -> str:
    """Generates a unique slug link.

    This function will loop recursively on itself to make sure the slug
    generated is unique.

    """
    slug = secrets.token_urlsafe(15)
    if not Entries.query.filter_by(slug_link=slug).first():
        return slug
    return _generate_unique_slug()


def create_secret(
    passphrase: str, secret: str, expire: int, tries: int, haveibeenpwned: bool
) -> Tuple[Dict, int]:
    """Create a secret.

    Args:
        passphrase (str): Passphrase needed to encrypt the secret.
        secret (str): Secret to encrypt.
        expire (int): Number of days the secret will be stored.
        tries (int): Number of tries to read the secret before it gets deleted.
        haveibeenpwned (bool): Passphrase has been checked with haveibeenpwned.

    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exp_date = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(days=expire)

    slug = _generate_unique_slug()
    Entries.create(
        slug_link=slug,
        encrypted_text=Secret(secret.encode(), passphrase).encrypt(),
        date_created=now,
        date_expires=exp_date,
        tries=tries,
        haveibeenpwned=haveibeenpwned,
    )

    app.logger.info(f"{slug} created and expires on {exp_date}")
    timez = datetime.now(timezone.utc).astimezone().tzname()
    response = {
        "status": Status.CREATED.value,
        "details": "Secret successfully created.",
        "slug": slug,
        "link": f"{request.url_root}r/{slug}",
        "expires_on": f"{exp_date.strftime('%Y-%m-%d at %H:%M')} {timez}",
    }
    return (response, HTTPStatus.CREATED.value)
