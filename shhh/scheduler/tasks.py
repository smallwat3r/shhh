from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from shhh.constants import ClientType
from shhh.domain import model
from shhh.extensions import db, scheduler
from shhh.liveness import db_liveness_ping

if TYPE_CHECKING:
    from typing import Iterable

logger = logging.getLogger("tasks")


@db_liveness_ping(ClientType.TASK)
def delete_expired_records() -> None:
    """Delete expired secrets from the database."""
    with scheduler.app.app_context():
        expired_secrets = db.session.query(model.Secret).filter(
            model.Secret.has_expired()).all()
        _delete_records(expired_secrets)
        logger.info("%s expired records have been deleted.",
                    len(expired_secrets))


def _delete_records(records: Iterable[model.Secret]) -> None:
    for record in records:
        db.session.delete(record)
    db.session.commit()
