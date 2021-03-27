import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from shhh.models import Entries


def generate_unique_slug() -> str:
    """Generates a unique slug link.

    This function will loop recursively on itself to make sure the slug
    generated is unique.

    """
    slug = secrets.token_urlsafe(15)
    if not Entries.query.filter_by(slug_link=slug).first():
        return slug
    return generate_unique_slug()


class Secret:
    """Secrets encryption / decryption management."""

    __slots__ = ("secret", "passphrase")

    def __init__(self, secret: bytes, passphrase: str):
        self.secret = secret
        self.passphrase = passphrase

    def __derive_key(self, salt: bytes, iterations: int) -> bytes:
        """Derive a secret key from a given passphrase and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return urlsafe_b64encode(kdf.derive(self.passphrase.encode()))

    def encrypt(self, iterations: int = 100_000) -> bytes:
        """Encrypt secret."""
        salt = secrets.token_bytes(16)
        key = self.__derive_key(salt, iterations)
        return urlsafe_b64encode(
            b"%b%b%b"
            % (
                salt,
                iterations.to_bytes(4, "big"),
                urlsafe_b64decode(Fernet(key).encrypt(self.secret)),
            )
        )

    def decrypt(self) -> str:
        """Decrypt secret."""
        decoded = urlsafe_b64decode(self.secret)
        salt, iteration, message = (
            decoded[:16],
            decoded[16:20],
            urlsafe_b64encode(decoded[20:]),
        )
        iterations = int.from_bytes(iteration, "big")
        key = self.__derive_key(salt, iterations)
        return Fernet(key).decrypt(message).decode("utf-8")
