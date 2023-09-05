import logging
import time
from http import HTTPStatus
from typing import Callable, NoReturn, TypeVar

from flask import Flask, Response, abort, current_app as app, make_response

from shhh.api.responses import ErrorResponse, Message
from shhh.constants import ClientType
from shhh.domain import model
from shhh.extensions import db, scheduler

logger = logging.getLogger(__name__)


def _get_retries_configs(flask_app: Flask) -> tuple[int, float]:
    return (flask_app.config["SHHH_DB_LIVENESS_RETRY_COUNT"],
            flask_app.config["SHHH_DB_LIVENESS_SLEEP_INTERVAL"])


def _perform_dummy_db_query() -> None:
    _ = db.session.query(model.Secret).first()


def _can_reach_db(flask_app: Flask) -> bool:
    retry_count, retry_sleep_interval_sec = _get_retries_configs(flask_app)

    for _ in range(retry_count):
        try:
            _perform_dummy_db_query()
            return True
        except Exception as err:
            logger.info("Retrying to reach database...")
            time.sleep(retry_sleep_interval_sec)
            exception = err

    logger.critical("There seems to be an issue with reaching the database")
    logger.exception(exception)
    return False


RT = TypeVar('RT')


def _check_task_liveness(f: Callable[..., RT], *args, **kwargs) -> RT | None:
    scheduler_app = scheduler.app
    with scheduler_app.app_context():
        if _can_reach_db(scheduler_app):
            return f(*args, **kwargs)

    return None


def _check_web_liveness(f: Callable[..., RT], *args,
                        **kwargs) -> RT | Response:
    if _can_reach_db(app):
        return f(*args, **kwargs)

    response = ErrorResponse(Message.UNEXPECTED)
    return abort(make_response(response.make(),
                               HTTPStatus.SERVICE_UNAVAILABLE))


def _check_liveness(client_type: ClientType,
                    f: Callable[..., Callable[..., RT]],
                    *args,
                    **kwargs) -> Callable[..., RT] | Response | None:

    def raise_no_implementation(*args, **kwargs) -> NoReturn:
        raise RuntimeError(f"No implementation found for {client_type}")

    factory = {
        ClientType.WEB: _check_web_liveness,
        ClientType.TASK: _check_task_liveness,
    }

    func = factory.get(client_type, raise_no_implementation)
    return func(f, *args, **kwargs)


def db_liveness_ping(
        client: ClientType
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Database liveness ping decorator.

    Some database might go to sleep if no recent activity is recorded (for
    example this is the case on some Heroku free plans). This decorator is
    used to run a dummy query against the database to make sure it's up and
    running before starting processing requests.
    """

    def inner(f):

        def wrapper(*args, **kwargs):
            return _check_liveness(client, f, *args, **kwargs)

        return wrapper

    return inner
