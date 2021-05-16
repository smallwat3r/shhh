import html
import secrets
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Tuple

from cryptography.fernet import InvalidToken
from flask import current_app as app

from shhh.api.encryption import Secret
from shhh.api.responses import ErrorResponse, Message, ReadResponse, Status, WriteResponse
from shhh.decorators import LivenessClient, db_liveness_ping
from shhh.models import Entries


@db_liveness_ping(LivenessClient.WEB.value)
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
            ReadResponse(Status.EXPIRED, Message.NOT_FOUND.value),
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
                ReadResponse(Status.INVALID, Message.EXCEEDED.value),
                HTTPStatus.UNAUTHORIZED.value,
            )

        secret.update(tries=remaining)
        app.logger.info(f"{slug} wrong passphrase used. Number of tries remaining: {remaining}")
        return (
            ReadResponse(
                Status.INVALID,
                Message.INVALID.value.format(remaining=remaining),
            ),
            HTTPStatus.UNAUTHORIZED.value,
        )

    secret.delete()  # Delete message after it's read
    app.logger.info(f"{slug} was decrypted and deleted")
    return (
        ReadResponse(Status.SUCCESS, html.escape(msg)),
        HTTPStatus.OK.value,
    )


def _generate_unique_slug() -> str:
    """Generates a unique slug link.

    This function will loop recursively on itself to make sure the slug
    generated is unique.

    """
    slug = secrets.token_urlsafe(15)
    if not Entries.query.filter_by(slug_link=slug).first():
        return slug

    return _generate_unique_slug()


@db_liveness_ping(LivenessClient.WEB.value)
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
    expires_on = f"{exp_date.strftime('%Y-%m-%d at %H:%M')} {timez}"

    return (WriteResponse(slug, expires_on), HTTPStatus.CREATED.value)


def parse_error(errors) -> Tuple[ErrorResponse, int]:
    """Parse API errors."""
    error = ""
    for source in ("json", "query"):
        for _, message in errors.messages.get(source, {}).items():
            error += f"{message[0]} "

    return (ErrorResponse(error), HTTPStatus.UNPROCESSABLE_ENTITY.value)
