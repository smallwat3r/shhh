import hashlib

import requests


def pwned_password(passphrase):
    """Check passphrase with Tory's Hunt haveibeenpwned API."""
    hasher = hashlib.sha1()
    hasher.update(passphrase.encode("utf-8"))
    digest = hasher.hexdigest().upper()

    r = requests.get(f"https://api.pwnedpasswords.com/range/{digest[:5]}",
                     timeout=5)
    r.raise_for_status()

    # yapf: disable
    pw_list = r.text.split("\n")
    return next(
        (int(e.split(":")[1]) for e in pw_list
         if (e.split(":")[0] == digest[5:])), False)
