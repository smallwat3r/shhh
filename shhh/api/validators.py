import enum
import re

from flask import current_app as app
from marshmallow import ValidationError
from shhh.api import utils
from webargs.flaskparser import abort, parser


@enum.unique
class Status(enum.Enum):
    """API body response statuses."""

    CREATED = "created"
    SUCCESS = "success"
    EXPIRED = "expired"
    INVALID = "invalid"
    ERROR = "error"


@parser.error_handler
def handle_parsing_error(err, req, schema, *, error_status_code, error_headers):  # pylint: disable=unused-argument
    """Handle request parsing errors."""
    abort(error_status_code,
          response=dict(details=err.messages, status=Status.ERROR.value))


def validate_strength(passphrase):
    """Passphrase strength validation handler.

    Minimum 8 characters containing at least one number and one uppercase.
    Query haveibeenpwned.com/passwords to check if the passphrase as already
    been pwned.

    """
    if passphrase:
        regex = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$")
        if not regex.search(passphrase) is not None:
            raise ValidationError(
                "Passphrase too weak. Minimun 8 characters, including "
                "1 number and 1 uppercase.")

    try:
        times_pwned = utils.pwned_password(passphrase)
    except Exception as err:  # pylint: disable=broad-except
        app.logger.error(err)
        times_pwned = None  # don't break if service isn't reachable.

    if times_pwned:
        raise ValidationError(
            f"This password has been pwned {times_pwned} times "
            "(haveibeenpwned.com), please chose another one.")


def validate_secret(secret):
    """Secret validation handler."""
    if not secret:
        raise ValidationError("Missing a secret to encrypt.")
    if len(secret) > 150:
        raise ValidationError(
            "The secret needs to have less than 150 characters.")


def validate_passphrase(passphrase):
    """Passphrase validation handler."""
    if not passphrase:
        raise ValidationError("Missing a passphrase.")


def validate_days(days):
    """Expiration validation handler."""
    if days == 0:
        raise ValidationError(
            "The minimum number of days to keep the secret alive is 1.")
    if days > 7:
        raise ValidationError(
            "The maximum number of days to keep the secret alive is 7.")


def validate_slug(slug):
    """Link validation handler."""
    if not slug:
        raise ValidationError("Missing a secret link.")
