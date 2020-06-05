import hashlib
from typing import Union

import requests


def pwned_password(passphrase: str) -> Union[int, bool]:
    """Check passphrase with Troy's Hunt haveibeenpwned API.

    Query the API to check if the passphrase has already been pwned in the
    past. If it has, returns the number of times it has been pwned, else
    returns False.

    Notes:
        (source haveibeenpwned.com)

        (...) implements a k-Anonymity model that allows a password to be
        searched for by partial hash. This allows the first 5 characters of a
        SHA-1 password hash (not case-sensitive) to be passed to the API.

        When a password hash with the same first 5 characters is found in the
        Pwned Passwords repository, the API will respond with an HTTP 200 and
        include the suffix of every hash beginning with the specified prefix,
        followed by a count of how many times it appears in the data set. The
        API consumer can then search the results of the response for the
        presence of their source hash.

    """
    # See nosec exclusion explanation in function docstring, we are cropping
    # the hash to use a k-Anonymity model to retrieve the pwned passwords.
    hasher = hashlib.sha1()  # nosec
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
