from __future__ import annotations

import logging
import time
from http import HTTPStatus
from typing import TYPE_CHECKING

from flask import abort, current_app as app, make_response
from sqlalchemy import text

from shhh.api.schemas import ErrorResponse
from shhh.constants import ClientType, Message
from shhh.extensions import db, scheduler

if TYPE_CHECKING:
    from typing import Callable, TypeVar

    from flask import Flask, Response

    RT = TypeVar('RT')

logger = logging.getLogger(__name__)


def _perform_db_connectivity_query() -> None:
    db.session.execute(text("SELECT 1;"))


def _check_table_exists(table_name: str) -> bool:
    return bool(db.inspect(db.engine).has_table(table_name))


def _get_retries_configs(flask_app: Flask) -> tuple[int, float]:
    return (flask_app.config["SHHH_DB_LIVENESS_RETRY_COUNT"],
            flask_app.config["SHHH_DB_LIVENESS_SLEEP_INTERVAL"])


def _is_db_awake(flask_app: Flask) -> bool:
    retry_count, retry_sleep_interval_sec = _get_retries_configs(flask_app)

    for _ in range(retry_count):
        try:
            _perform_db_connectivity_query()
            return True
        except Exception as exc:
            logger.info("Retrying to reach database...")
            time.sleep(retry_sleep_interval_sec)
            exception = exc

    logger.critical("Could not reach the database, something is wrong "
                    "with the database connection")
    logger.exception(exception)
    return False


def _is_db_table_up(flask_app: Flask) -> bool:
    if _check_table_exists("secret"):
        return True
    logger.critical("Could not query required table 'secret', make sure it "
                    "has been created on the database")
    return False


def _is_db_healthy(flask_app: Flask) -> bool:
    return _is_db_awake(flask_app) and _is_db_table_up(flask_app)


def _check_task_liveness(f: Callable[..., RT], *args, **kwargs) -> RT | None:
    scheduler_app = scheduler.app
    with scheduler_app.app_context():
        if _is_db_healthy(scheduler_app):
            return f(*args, **kwargs)

    return None


def _check_web_liveness(f: Callable[..., RT], *args,
                        **kwargs) -> RT | Response:
    if _is_db_healthy(app):
        return f(*args, **kwargs)

    response = ErrorResponse(Message.UNEXPECTED)
    abort(make_response(response(), HTTPStatus.SERVICE_UNAVAILABLE))


def _check_liveness(client_type: ClientType,
                    f: Callable[..., Callable[..., RT]],
                    *args,
                    **kwargs) -> Callable[..., RT] | Response | None:

    if client_type not in set(ClientType):
        raise RuntimeError(f"No implementation found for {client_type=}")

    factory = {
        ClientType.WEB: _check_web_liveness,
        ClientType.TASK: _check_task_liveness,
    }
    func = factory[client_type]
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
