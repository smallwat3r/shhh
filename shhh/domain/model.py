import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta

from sqlalchemy.ext.hybrid import hybrid_method

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from shhh.constants import DEFAULT_READ_TRIES_VALUE


class Secret:
    """Domain model for secrets."""

    # pylint: disable=too-many-arguments
    def __init__(self,
                 encrypted_text: bytes,
                 date_created: datetime,
                 date_expires: datetime,
                 external_id: str,
                 tries: int) -> None:
        self.encrypted_text = encrypted_text
        self.date_created = date_created
        self.date_expires = date_expires
        self.external_id = external_id
        self.tries = tries

    def __repr__(self) -> str:
        return f"<Secret {self.external_id} (expires: {self.date_expires})>"

    @staticmethod
    def _derive_key(passphrase: str, salt: bytes, iterations: int) -> bytes:
        """Derive a secret key from a given passphrase and salt."""
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=32,
                         salt=salt,
                         iterations=iterations,
                         backend=default_backend())
        return urlsafe_b64encode(kdf.derive(passphrase.encode()))

    @staticmethod
    def _set_expiry_date(from_date: datetime, expire: str) -> datetime:
        units = {"m": "minutes", "h": "hours", "d": "days"}
        timedelta_parameters = {}
        for unit, parameter in units.items():
            if not expire.endswith(unit):
                continue
            timedelta_parameters = {parameter: int(expire.split(unit)[0])}
            return from_date + timedelta(**timedelta_parameters)
        raise RuntimeError(f"Could not set expiry date for code {expire}")

    @classmethod
    def encrypt(cls,
                message: str,
                passphrase: str,
                expire_code: str,
                tries: int = DEFAULT_READ_TRIES_VALUE,
                iterations: int = 100_000) -> "Secret":
        salt = secrets.token_bytes(16)
        key = cls._derive_key(passphrase, salt, iterations)
        encrypted_text = urlsafe_b64encode(
            b"%b%b%b" %
            (salt,
             iterations.to_bytes(4, "big"),
             urlsafe_b64decode(Fernet(key).encrypt(message.encode()))))
        now = datetime.utcnow()
        return cls(encrypted_text=encrypted_text,
                   date_created=now,
                   date_expires=cls._set_expiry_date(from_date=now,
                                                     expire=expire_code),
                   external_id=secrets.token_urlsafe(15),
                   tries=tries)

    def decrypt(self, passphrase: str) -> str:
        decoded = urlsafe_b64decode(self.encrypted_text)
        salt, iteration, message = (
            decoded[:16],
            decoded[16:20],
            urlsafe_b64encode(decoded[20:]),
        )
        iterations = int.from_bytes(iteration, "big")
        key = self._derive_key(passphrase, salt, iterations)
        return Fernet(key).decrypt(message).decode("utf-8")

    @property
    def expires_on_text(self) -> str:
        timez = datetime.utcnow().astimezone().tzname()
        return f"{self.date_expires.strftime('%B %d, %Y at %H:%M')} {timez}"

    @hybrid_method
    def has_expired(self) -> bool:
        return self.date_expires <= datetime.now()

    @hybrid_method
    def has_external_id(self, external_id: str) -> bool:
        return self.external_id == external_id
