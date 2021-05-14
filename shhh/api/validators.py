# pylint: disable=unused-argument
import enum
import re
from http import HTTPStatus

from flask import current_app as app
from flask import jsonify, make_response
from marshmallow import ValidationError
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
    error = ""
    for source in ("json", "query"):
        for _, message in err.messages.get(source, {}).items():
            error += f"{message[0]} "

    response = {"response": {"details": error, "status": Status.ERROR.value}}
    return abort(
        make_response(
            jsonify(response),
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )
    )


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
                    "Passphrase too weak. Minimun 8 characters, including 1 number and 1 uppercase."
                )

    @classmethod
    def haveibeenpwned(cls, passphrase: str) -> None:
        """Validate passphrase against haveibeenpwned API."""
        try:
            times_pwned = services.pwned_password(passphrase)
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
    def days(cls, days: int) -> None:
        """Expiration validation handler."""
        if days <= 0:
            raise ValidationError("The minimum number of days to keep the secret alive is 1.")
        if days > 7:
            raise ValidationError("The maximum number of days to keep the secret alive is 7.")

    @classmethod
    def tries(cls, tries: int) -> None:
        """Maximum tries validation handler."""
        if tries < 3:
            raise ValidationError("The minimum number of tries to decrypt the secret is 3.")
        if tries > 10:
            raise ValidationError("The maximum number of tries to decrypt the secret is 10.")

    @classmethod
    def slug(cls, slug: str) -> None:
        """Link validation handler."""
        if not slug:
            raise ValidationError("Missing a secret link.")
