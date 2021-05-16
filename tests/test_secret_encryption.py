import unittest

from cryptography.fernet import InvalidToken

from shhh.api.encryption import Secret


class TestSecretEncryption(unittest.TestCase):
    """Encryption testing."""

    secret = "I'm a secret message."
    passphrase = "SuperSecret123"
    encrypted_text = (
        b"nKir73XhgyXxjwYyCG-QHQABhqCAAAAAAF6rPvPYX7OYFZRTzy"
        b"PdIwvdo2SFwAN0VXrfosL54nGHr0MN1YtyoNjx4t5Y6058lFvDH"
        b"zsnv_Q1KaGFL6adJgLLVreOZ9kt5HpwnEe_Lod5Or85Ig=="
    )

    def test_unique_encryption(self):
        encrypted = Secret(self.secret.encode(), self.passphrase).encrypt()
        self.assertNotEqual(encrypted, self.encrypted_text)

    def test_wrong_passphrase(self):
        with self.assertRaises(InvalidToken):
            Secret(self.encrypted_text, "wrongPassphrase").decrypt()

    def test_decryption(self):
        self.assertEqual(Secret(self.encrypted_text, self.passphrase).decrypt(), self.secret)


if __name__ == "__main__":
    unittest.main()
