import re
import secrets

from shhh.extensions import db
from shhh.models import Slugs


def passphrase_strength(passphrase):
    """Check the passphrase strength.

    Requirements: Min 8 chars, one number, one uppercase.

    """
    return (len(passphrase) >= 8 and re.search("[0-9]", passphrase) is not None
            and re.search("[A-Z]", passphrase) is not None)


def generate_unique_slug():
    """Generates a unique slug link.

    This function will loop recursively if the new slug generated isn't unique.

    """
    slug = secrets.token_urlsafe(15)
    if not db.session.query(Slugs).filter_by(slug_link=slug).first():
        return slug
    return generate_unique_slug()
