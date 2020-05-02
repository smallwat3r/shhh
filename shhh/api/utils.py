import hashlib

import requests


def pwned_password(passphrase):
    """Check passphrase with Tory's Hunt haveibeenpwned API.

    Query the API to check if the passphrase has already been pwned in the
    past. If it has, returns the first match from generator, else returns
    False.

    """
    hasher = hashlib.sha1()
    hasher.update(passphrase.encode("utf-8"))
    digest = hasher.hexdigest().upper()

    endpoint = f"https://api.pwnedpasswords.com/range"
    r = requests.get(f"{endpoint}/{digest[:5]}", timeout=5)
    r.raise_for_status()

    # yapf: disable
    return next(
        (
            int(e.split(":")[1])
            for e in r.text.split("\n")
            if e.split(":")[0] == digest[5:]
        ),
        False
    )
