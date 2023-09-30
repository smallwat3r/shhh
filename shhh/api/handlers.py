from __future__ import annotations

from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import TYPE_CHECKING

from cryptography.fernet import InvalidToken
from flask import current_app as app, make_response
from sqlalchemy.orm.exc import NoResultFound

from shhh.api.schemas import ErrorResponse, ReadResponse, WriteResponse
from shhh.constants import ClientType, Message, Status
from shhh.domain import model
from shhh.extensions import db
from shhh.liveness import db_liveness_ping

if TYPE_CHECKING:
    from flask import Response
    from marshmallow import ValidationError

    from shhh.api.schemas import CallableResponse


class Handler(ABC):

    @abstractmethod
    def handle(self) -> tuple[CallableResponse, HTTPStatus]:
        pass

    def make_response(self) -> Response:
        response, code = self.handle()
        return make_response(response(), code)


class ReadHandler(Handler):

    def __init__(self, external_id: str, passphrase: str) -> None:
        self.external_id = external_id
        self.passphrase = passphrase

    @db_liveness_ping(ClientType.WEB)
    def handle(self) -> tuple[ReadResponse, HTTPStatus]:
        try:
            secret = db.session.query(model.Secret).filter(
                model.Secret.has_external_id(self.external_id)).one()
        except NoResultFound:
            return (ReadResponse(Status.EXPIRED, Message.NOT_FOUND),
                    HTTPStatus.NOT_FOUND)

        try:
            message = secret.decrypt(self.passphrase)
        except InvalidToken:
            remaining = secret.tries - 1
            if remaining == 0:
                # number of tries exceeded, delete secret
                app.logger.info("%s tries to open secret exceeded",
                                str(secret))
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
                Status.INVALID,
                Message.INVALID.value.format(remaining=remaining)),
                    HTTPStatus.UNAUTHORIZED)

        db.session.delete(secret)
        db.session.commit()
        app.logger.info("%s was decrypted and deleted", str(secret))
        return ReadResponse(Status.SUCCESS, message), HTTPStatus.OK


class WriteHandler(Handler):

    def __init__(self, passphrase: str, secret: str, expire: str,
                 tries: int) -> None:
        self.passphrase = passphrase
        self.secret = secret
        self.expire = expire
        self.tries = tries

    @db_liveness_ping(ClientType.WEB)
    def handle(self) -> tuple[WriteResponse, HTTPStatus]:
        encrypted_secret = model.Secret.encrypt(message=self.secret,
                                                passphrase=self.passphrase,
                                                expire_code=self.expire,
                                                tries=self.tries)
        db.session.add(encrypted_secret)
        db.session.commit()
        app.logger.info("%s created", str(encrypted_secret))
        return (WriteResponse(encrypted_secret.external_id,
                              encrypted_secret.expires_on_text),
                HTTPStatus.CREATED)


class ErrorHandler(Handler):

    def __init__(self, error_exc: ValidationError) -> None:
        self.error_exc = error_exc

    def handle(self) -> tuple[ErrorResponse, HTTPStatus]:
        messages = self.error_exc.normalized_messages()
        error = ""
        for source in ("json", "query"):
            for _, message in messages.get(source, {}).items():
                error += f"{message[0]} "
        return ErrorResponse(error.strip()), HTTPStatus.UNPROCESSABLE_ENTITY
