from datetime import datetime, timedelta, timezone

from flask import request

from ..config.api_config import Status
from ... import logger
from ...utils import database, util
from ...utils.encryption import Secret


def create_secret(passphrase, secret, expire):
    """Create a secret."""
    if not secret or secret == "":
        return {
            "status": Status.ERROR.value,
            "details": "You need to enter a secret to encrypt."
        }

    if len(secret) > 150:
        return {
            "status": Status.ERROR.value,
            "details": "Your secret needs to have less than 150 characters."
        }

    if not passphrase:
        return {
            "status":
                Status.ERROR.value,
            "details":
                ("Please enter a passphrase. "
                 "It needs minimun 5 characters, 1 number and 1 uppercase.")
        }

    if not util.passphrase_strength(passphrase):
        return {
            "status":
                Status.ERROR.value,
            "details":
                ("The passphrase you used is too weak. "
                 "It needs minimun 5 characters, 1 number and 1 uppercase.")
        }

    if expire > 7:
        return {
            "status":
                Status.ERROR.value,
            "details":
                "The maximum number of days to keep the secret alive is 7."
        }

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    expires = datetime.strptime(now,
                                "%Y-%m-%d %H:%M:%S") + timedelta(days=expire)

    with database.DbConn() as db:
        slug = util.generate_unique_slug(db)
        db.commit(
            "store_encrypt.sql",
            {
                "slug_link": slug,
                "encrypted_text": Secret(secret.encode(), passphrase).encrypt(),
                "date_created": now,
                "date_expires": expires
            })

    logger.info(f"{slug} created and expires on {expires}")
    timez = datetime.now(timezone.utc).astimezone().tzname()
    return {
        "status": Status.CREATED.value,
        "details": "Secret successfully created.",
        "slug": slug,
        "link": f"{request.url_root}r/{slug}",
        "expires_on": f"{expires.strftime('%Y-%m-%d at %H:%M')} {timez}"
    }
