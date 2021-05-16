import enum
import logging
import time
from http import HTTPStatus

from flask import abort, make_response
from flask import current_app as app
from sqlalchemy.exc import OperationalError

from shhh.api.responses import ErrorResponse, Message
from shhh.extensions import db, scheduler

logger = logging.getLogger(__name__)


class LivenessClient(enum.Enum):
    """Liveness client type."""

    WEB = "web"
    TASK = "task"


def db_liveness_ping(client):
    """Database liveness ping decorator.

    Some database might go to sleep if no recent activity is recorded (for example this is
    the case on some Heroku free plans). This decorator is used to send pings to the database
    to make sure it's up and running before starting processing requests.

    """

    def inner(f):
        """Inner function."""

        def wrapper(*args, **kwargs):
            """Wrapper function."""

            if client == LivenessClient.TASK.value:
                scheduler_app = scheduler.app
                with scheduler_app.app_context():
                    retry_count = app.config["SHHH_DB_LIVENESS_RETRY_COUNT"]
                    retry_sleep_interval_sec = app.config["SHHH_DB_LIVENESS_SLEEP_INTERVAL"]
            else:
                retry_count = app.config["SHHH_DB_LIVENESS_RETRY_COUNT"]
                retry_sleep_interval_sec = app.config["SHHH_DB_LIVENESS_SLEEP_INTERVAL"]

            for _ in range(retry_count):
                try:
                    # Check if we can reach the database and perform an operation against it.
                    if client == LivenessClient.TASK.value:
                        with scheduler_app.app_context():
                            db.session.rollback()
                    else:
                        db.session.rollback()
                    return f(*args, **kwargs)
                except OperationalError:
                    logger.info("Retrying to reach database...")
                    time.sleep(retry_sleep_interval_sec)

            logger.critical("Database seems down and couldn't wake up.")

            # If liveness check is coming from the scheduler, ignore client response.
            if client == LivenessClient.TASK.value:
                return None

            response = ErrorResponse(Message.UNEXPECTED.value)
            return abort(make_response(response.make(), HTTPStatus.SERVICE_UNAVAILABLE.value))

        return wrapper

    return inner
