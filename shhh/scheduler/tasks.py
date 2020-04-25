from datetime import datetime

from shhh.extensions import db, scheduler
from shhh.models import Entries


def delete_expired_links():
    """Delete expired links from the database."""
    app = scheduler.app

    with app.app_context():
        db.session.query(Entries).filter(
            Entries.date_expires <= datetime.now()).delete()
        db.session.commit()
