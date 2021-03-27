import html
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Tuple

from cryptography.fernet import InvalidToken
from flask import current_app as app
from flask import jsonify, request

from shhh.api.constants import Messages
from shhh.api.utils import Secret, generate_unique_slug
from shhh.api.validators import Status
from shhh.models import Entries


@dataclass
class ReadResponse:
    """Read client response schema."""

    status: str
    msg: str

    def make(self):
        """Make client response object."""
        return jsonify({"response": {"status": self.status, "msg": self.msg}})


@dataclass
class WriteResponse:
    """Write client response schema."""

    status: str
    details: str
    slug: str
    expires_on: str
    link: str = field(init=False)

    def __post_init__(self):
        self.link = f"{request.url_root}r/{self.slug}"
        if _host := app.config["SHHH_HOST"]:
            self.link = f"{_host.rstrip('/')}/r/{self.slug}"

    def make(self):
        """Make client response object."""
        return jsonify(
            {
                "response": {
                    "status": self.status,
                    "details": self.details,
                    "slug": self.slug,
                    "link": self.link,
                    "expires_on": self.expires_on,
                }
            }
        )


def read_secret(slug: str, passphrase: str) -> Tuple[ReadResponse, int]:
    """Read a secret.

    Args:
        slug (str): Unique slug link to access the secret.
        passphrase (str): Passphrase needed to decrypt the secret.

    """
    secret = Entries.query.filter_by(slug_link=slug).first()
    if not secret:
        app.logger.info(f"{slug} tried to read but do not exists in database")
        return (
            ReadResponse(Status.EXPIRED.value, Messages.NOT_FOUND.value),
            HTTPStatus.NOT_FOUND.value,
        )

    try:
        msg = Secret(secret.encrypted_text, passphrase).decrypt()
    except InvalidToken:
        remaining = secret.tries - 1
        if remaining == 0:
            # Number of tries exceeded, delete secret
            app.logger.warning(f"{slug} tries to open secret exceeded")
            secret.delete()
            return (
                ReadResponse(Status.INVALID.value, Messages.EXCEEDED.value),
                HTTPStatus.UNAUTHORIZED.value,
            )

        secret.update(tries=remaining)
        app.logger.info(f"{slug} wrong passphrase used. Number of tries remaining: {remaining}")
        return (
            ReadResponse(Status.INVALID.value, Messages.INVALID.value.format(remaining=remaining),),
            HTTPStatus.UNAUTHORIZED.value,
        )

    secret.delete()  # Delete message after it's read
    app.logger.info(f"{slug} was decrypted and deleted")
    return (
        ReadResponse(Status.SUCCESS.value, html.escape(msg)),
        HTTPStatus.OK.value,
    )


def write_secret(
    passphrase: str, secret: str, expire: int, tries: int, haveibeenpwned: bool
) -> Tuple[WriteResponse, int]:
    """Write a secret.

    Args:
        passphrase (str): Passphrase needed to encrypt the secret.
        secret (str): Secret to encrypt.
        expire (int): Number of days the secret will be stored.
        tries (int): Number of tries to read the secret before it gets deleted.
        haveibeenpwned (bool): Passphrase has been checked with haveibeenpwned.

    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exp_date = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(days=expire)

    slug = generate_unique_slug()
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

    expires_on = f"{exp_date.strftime('%Y-%m-%d at %H:%M')} {timez}"
    return (
        WriteResponse(Status.CREATED.value, Messages.CREATED.value, slug, expires_on),
        HTTPStatus.CREATED.value,
    )
