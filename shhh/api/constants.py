import enum


class Messages(enum.Enum):
    """Message constants."""

    NOT_FOUND = (
        "Sorry, we can't find a secret, it has expired, been deleted or has already been read."
    )
    EXCEEDED = (
        "The passphrase is not valid. You've exceeded the "
        "number of tries and the secret has been deleted."
    )
    INVALID = "Sorry the passphrase is not valid. Number of tries remaining {remaining}."
    CREATED = "Secret successfully created."
