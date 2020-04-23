import re
import secrets


def passphrase_strength(passphrase):
    """Check the passphrase strength.

    Requirements: Min 5 chars, one number, one uppercase.
    """
    return (len(passphrase) >= 5 and re.search("[0-9]", passphrase) is not None
            and re.search("[A-Z]", passphrase) is not None)


def generate_unique_slug(db):
    """Generates a unique slug link."""
    slug = secrets.token_urlsafe(15)
    exists = db.get("check_slug_availability.sql", {"slug_link": slug})
    if not exists:
        return slug

    return generate_unique_slug(db)
