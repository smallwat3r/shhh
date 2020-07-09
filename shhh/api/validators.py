# pylint: disable=unused-argument
import enum
import re
from http import HTTPStatus

from marshmallow import ValidationError
from flask import current_app as app
from webargs.flaskparser import abort, parser

from shhh.api import services


@enum.unique
class Status(enum.Enum):
    """API body response statuses."""

    CREATED = "created"
    SUCCESS = "success"
    EXPIRED = "expired"
    INVALID = "invalid"
    ERROR = "error"


@parser.error_handler
def handle_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """Handle request parsing errors."""
    abort(
        HTTPStatus.UNPROCESSABLE_ENTITY.value,
        response=dict(details=err.messages, status=Status.ERROR.value),
    )


def validate_strength(passphrase: str) -> None:
    """Passphrase strength validation handler.

    Minimum 8 characters containing at least one number and one uppercase.

    """
    if passphrase:
        regex = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$")
        if not regex.search(passphrase) is not None:
            raise ValidationError(
                "Passphrase too weak. Minimun 8 characters, including "
                "1 number and 1 uppercase."
            )


def validate_haveibeenpwned(passphrase: str) -> None:
    """Validate passphrase against haveibeenpwned API."""
    try:
        times_pwned = services.pwned_password(passphrase)
    except Exception as err:  # pylint: disable=broad-except
        app.logger.error(err)
        times_pwned = False  # don't break if service isn't reachable.

    if times_pwned:
        raise ValidationError(
            f"This password has been pwned {times_pwned} times "
            "(haveibeenpwned.com), please chose another one."
        )


def validate_secret(secret: str) -> None:
    """Secret validation handler."""
    if not secret:
        raise ValidationError("Missing a secret to encrypt.")
    if len(secret) > 150:
        raise ValidationError("The secret needs to have less than 150 characters.")


def validate_passphrase(passphrase: str) -> None:
    """Passphrase validation handler."""
    if not passphrase:
        raise ValidationError("Missing a passphrase.")


def validate_days(days: int) -> None:
    """Expiration validation handler."""
    if days == 0:
        raise ValidationError(
            "The minimum number of days to keep the secret alive is 1."
        )
    if days > 7:
        raise ValidationError(
            "The maximum number of days to keep the secret alive is 7."
        )


def validate_tries(tries: int) -> None:
    """Maximum tries validation handler."""
    if tries < 3:
        raise ValidationError("The minimum number of tries to decrypt the secret is 3.")
    if tries > 10:
        raise ValidationError(
            "The maximum number of tries to decrypt the secret is 10."
        )


def validate_slug(slug: str) -> None:
    """Link validation handler."""
    if not slug:
        raise ValidationError("Missing a secret link.")
