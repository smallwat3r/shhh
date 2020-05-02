import re
import unittest
from unittest import mock

from marshmallow import ValidationError

from shhh.api.validators import days, passphrase, secret, slug, strength


class TestValidators(unittest.TestCase):

    def test_secret(self):
        with self.assertRaises(ValidationError):
            secret(None)
            secret("")
            secret(151 * "*")

    def test_passphrase(self):
        with self.assertRaises(ValidationError):
            passphrase(None)
            passphrase("")

    def test_days(self):
        with self.assertRaises(ValidationError):
            days(0)
            days(8)

    def test_slug(self):
        with self.assertRaises(ValidationError):
            slug(None)
            slug("")

    @mock.patch('shhh.api.utils.pwned_password')
    def test_strength(self, mock_pwned):
        with self.assertRaises(ValidationError):
            strength("weak")
            strength("Weak")
            strength("Weak1")
            strength("weak_but_long")
            strength("weak_but_long_1")
            strength("Weak_but_long")

            mock_pwned.return_value = 123
            strength("Hello123")

            mock_pwned.side_effect = Exception
            strength("Hello123j0e32hf")
