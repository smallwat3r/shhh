from datetime import datetime

from shhh.extensions import scheduler
from shhh.models import Entries


def delete_expired_links():
    """Delete expired links from the database."""
    app = scheduler.app
    with app.app_context():
        expired = Entries.query.filter(Entries.date_expires <= datetime.now()).all()
        for record in expired:
            record.delete()
