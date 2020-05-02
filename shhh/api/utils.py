import hashlib

import requests


def pwned_password(passphrase):
    """Check passphrase with Troy's Hunt haveibeenpwned API.

    Query the API to check if the passphrase has already been pwned in the
    past. If it has, returns the number of times it has been pwned, else
    returns False.

    """
    hasher = hashlib.sha1()
    hasher.update(passphrase.encode("utf-8"))
    digest = hasher.hexdigest().upper()

    endpoint = "https://api.pwnedpasswords.com/range"
    r = requests.get(f"{endpoint}/{digest[:5]}", timeout=5)
    r.raise_for_status()

    for line in r.text.split('\n'):
        info = line.split(':')
        if info[0] == digest[5:]:
            return int(info[1])

    # Password hasn't been pwned.
    return False
