import html
import secrets
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Tuple

from cryptography.fernet import InvalidToken
from flask import current_app as app

from shhh.api.encryption import Secret
from shhh.api.responses import ErrorResponse, Message, ReadResponse, Status, WriteResponse
from shhh.enums import LivenessClient
from shhh.liveness import db_liveness_ping
from shhh.models import Entries


@db_liveness_ping(LivenessClient.WEB)
def read_secret(slug: str, passphrase: str) -> Tuple[ReadResponse, HTTPStatus]:
    """Read a secret.

    Args:
        slug (str): Unique slug link to access the secret.
        passphrase (str): Passphrase needed to decrypt the secret.

    """
    secret = Entries.query.filter_by(slug_link=slug).first()
    if not secret:
        app.logger.info(f"{slug} tried to read but do not exists in database")
        return (
            ReadResponse(Status.EXPIRED, Message.NOT_FOUND.value),
            HTTPStatus.NOT_FOUND,
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
                ReadResponse(Status.INVALID, Message.EXCEEDED.value),
                HTTPStatus.UNAUTHORIZED,
            )

        secret.update(tries=remaining)
        app.logger.info(f"{slug} wrong passphrase used. Number of tries remaining: {remaining}")
        return (
            ReadResponse(
                Status.INVALID,
                Message.INVALID.value.format(remaining=remaining),
            ),
            HTTPStatus.UNAUTHORIZED,
        )

    secret.delete()  # Delete message after it's read
    app.logger.info(f"{slug} was decrypted and deleted")
    return (
        ReadResponse(Status.SUCCESS, html.escape(msg, quote=False)),
        HTTPStatus.OK,
    )


def _generate_unique_slug() -> str:
    """Generates a unique slug link.

    This function will loop recursively on itself to make sure the slug
    generated is unique.

    """
    slug = secrets.token_urlsafe(15)
    if not Entries.query.filter_by(slug_link=slug).first():
        return slug

    return _generate_unique_slug()  # Edge case


def _build_expiry_date(now: str, expire: str) -> datetime:
    """Builds secret expiry date."""
    units = {"m": "minutes", "h": "hours", "d": "days"}

    timedelta_parameters = {}
    for unit, parameter in units.items():
        if expire.endswith(unit):
            timedelta_parameters = {parameter: int(expire.split(unit)[0])}
            break

    return datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(**timedelta_parameters)


@db_liveness_ping(LivenessClient.WEB)
def write_secret(
    passphrase: str, secret: str, expire: str, tries: int, haveibeenpwned: bool
) -> Tuple[WriteResponse, HTTPStatus]:
    """Write a secret.

    Args:
        passphrase (str): Passphrase needed to encrypt the secret.
        secret (str): Secret to encrypt.
        expire (int): How long the secret will be stored.
        tries (int): Number of tries to read the secret before it gets deleted.
        haveibeenpwned (bool): Passphrase has been checked with haveibeenpwned.

    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exp_date = _build_expiry_date(now, expire)
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
    expires_on = f"{exp_date.strftime('%B %d, %Y at %H:%M')} {timez}"

    return (WriteResponse(slug, expires_on), HTTPStatus.CREATED)


def parse_error(errors) -> Tuple[ErrorResponse, HTTPStatus]:
    """Parse API errors."""
    error = ""
    for source in ("json", "query"):
        for _, message in errors.messages.get(source, {}).items():
            error += f"{message[0]} "

    return (ErrorResponse(error), HTTPStatus.UNPROCESSABLE_ENTITY)
