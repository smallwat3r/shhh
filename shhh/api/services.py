import enum
import html
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import request, current_app as app
from marshmallow import Schema

from shhh.api import utils
from shhh.models import Slugs

from .. import db


@enum.unique
class Status(enum.Enum):
    """API statuses."""

    CREATED = "created"
    SUCCESS = "success"
    EXPIRED = "expired"
    ERROR = "error"


class Secret:
    """Secrets encryption / decryption management."""

    __slots__ = ("secret", "passphrase", )

    def __init__(self, secret, passphrase):
        self.secret = secret
        self.passphrase = passphrase

    def __derive_key(self, salt, iterations):
        """Derive a secret key from a given passphrase and salt."""
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=32,
                         salt=salt,
                         iterations=iterations,
                         backend=default_backend())
        return urlsafe_b64encode(kdf.derive(self.passphrase.encode()))

    def encrypt(self, iterations=100_000):
        """Encrypt secret."""
        salt = secrets.token_bytes(16)
        key = self.__derive_key(salt, iterations)
        return urlsafe_b64encode(
            b"%b%b%b" % (salt,
                         iterations.to_bytes(4, "big"),
                         urlsafe_b64decode(Fernet(key).encrypt(self.secret))))

    def decrypt(self):
        """Decrypt secret."""
        decoded = urlsafe_b64decode(self.secret)
        salt, iteration, message = (
            decoded[:16],
            decoded[16:20],
            urlsafe_b64encode(decoded[20:])
        )
        iterations = int.from_bytes(iteration, "big")
        key = self.__derive_key(salt, iterations)
        return Fernet(key).decrypt(message).decode("utf-8")


def read_secret(slug, passphrase):
    """Read a secret."""
    if not passphrase:
        return dict(status=Status.ERROR.value, msg="Please enter a passphrase.")
    secret = db.session.query(Slugs).filter_by(slug_link=slug).first()
    if not secret:
        app.logger.warning(
            f"{slug} tried to read but do not exists in database")
        return dict(status=Status.EXPIRED.value,
                    msg="Sorry the data has expired or has already been read.")
    try:
        msg = Secret(secret.encrypted_text, passphrase).decrypt()
    except InvalidToken:
        app.logger.warning(f"{slug} wrong passphrase used")
        return dict(status=Status.ERROR.value,
                    msg="Sorry the passphrase is not valid.")

    # Automatically delete message from the database.
    db.session.query(Slugs).filter_by(slug_link=slug).delete()
    db.session.commit()

    app.logger.info(f"{slug} was decrypted and deleted")
    return dict(status=Status.SUCCESS.value, msg=html.escape(msg))


def create_secret(passphrase, secret, expire):
    """Create a secret."""
    if not secret or secret == "":
        return dict(status=Status.ERROR.value,
                    details="You need to enter a secret to encrypt.")
    if len(secret) > 150:
        return dict(
            status=Status.ERROR.value,
            details="Your secret needs to have less than 150 characters.")
    if not passphrase:
        return dict(
            status=Status.ERROR.value,
            details=(
                "Please enter a passphrase. "
                "It needs minimun 5 characters, 1 number and 1 uppercase."))
    if not utils.passphrase_strength(passphrase):
        return dict(
            status=Status.ERROR.value,
            details=(
                "The passphrase you used is too weak. "
                "It needs minimun 8 characters, 1 number and 1 uppercase."))
    if expire > 7:
        return dict(
            status=Status.ERROR.value,
            details="The maximum number of days to keep the secret alive is 7.")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    expiration_date = datetime.strptime(
        now, "%Y-%m-%d %H:%M:%S") + timedelta(days=expire)

    slug = utils.generate_unique_slug()
    db.session.add(
        Slugs(slug_link=slug,
              encrypted_text=Secret(secret.encode(), passphrase).encrypt(),
              date_created=now,
              date_expires=expiration_date))
    db.session.commit()

    app.logger.info(f"{slug} created and expires on {expiration_date}")
    timez = datetime.now(timezone.utc).astimezone().tzname()
    return dict(
        status=Status.CREATED.value,
        details="Secret successfully created.",
        slug=slug,
        link=f"{request.url_root}r/{slug}",
        expires_on=f"{expiration_date.strftime('%Y-%m-%d at %H:%M')} {timez}")
