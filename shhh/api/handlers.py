from http import HTTPStatus

from cryptography.fernet import InvalidToken
from flask import current_app as app
from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from shhh.api.schemas import (ErrorResponse,
                              Message,
                              ReadResponse,
                              Status,
                              WriteResponse)
from shhh.constants import ClientType
from shhh.domain import model
from shhh.extensions import db
from shhh.liveness import db_liveness_ping


@db_liveness_ping(ClientType.WEB)
def read(external_id: str, passphrase: str) -> tuple[ReadResponse, HTTPStatus]:
    try:
        secret = db.session.query(model.Secret).filter(
            model.Secret.has_external_id(external_id)).one()
    except NoResultFound:
        return (ReadResponse(Status.EXPIRED, Message.NOT_FOUND),
                HTTPStatus.NOT_FOUND)

    try:
        message = secret.decrypt(passphrase)
    except InvalidToken:
        remaining = secret.tries - 1
        if remaining == 0:
            # number of tries exceeded, delete secret
            app.logger.info("%s tries to open secret exceeded", str(secret))
            db.session.delete(secret)
            db.session.commit()
            return (ReadResponse(Status.INVALID, Message.EXCEEDED),
                    HTTPStatus.UNAUTHORIZED)

        secret.tries = remaining
        db.session.commit()
        app.logger.info(
            "%s wrong passphrase used. Number of tries remaining: %s",
            str(secret),
            remaining)
        return (ReadResponse(
            Status.INVALID, Message.INVALID.value.format(remaining=remaining)),
                HTTPStatus.UNAUTHORIZED)

    db.session.delete(secret)
    db.session.commit()
    app.logger.info("%s was decrypted and deleted", str(secret))
    return ReadResponse(Status.SUCCESS, message), HTTPStatus.OK


@db_liveness_ping(ClientType.WEB)
def write(passphrase: str, secret: str, expire: str,
          tries: int) -> tuple[WriteResponse, HTTPStatus]:
    encrypted_secret = model.Secret.encrypt(message=secret,
                                            passphrase=passphrase,
                                            expire_code=expire,
                                            tries=tries)
    db.session.add(encrypted_secret)
    db.session.commit()
    app.logger.info("%s created", str(encrypted_secret))
    return (WriteResponse(encrypted_secret.external_id,
                          encrypted_secret.expires_on_text),
            HTTPStatus.CREATED)


def parse_error(
        error_exc: ValidationError) -> tuple[ErrorResponse, HTTPStatus]:
    messages = error_exc.normalized_messages()
    error = ""
    for source in ("json", "query"):
        for _, message in messages.get(source, {}).items():
            error += f"{message[0]} "
    return ErrorResponse(error.strip()), HTTPStatus.UNPROCESSABLE_ENTITY
