import re
import unittest
from unittest import mock

from marshmallow import ValidationError

from shhh.api.validators import (
    validate_days, validate_passphrase, validate_secret, validate_slug,
    validate_strength)


class TestValidators(unittest.TestCase):

    def test_secret(self):
        with self.assertRaises(ValidationError):
            validate_secret(None)
            validate_secret("")
            validate_secret(151 * "*")

    def test_passphrase(self):
        with self.assertRaises(ValidationError):
            validate_passphrase(None)
            validate_passphrase("")

    def test_days(self):
        with self.assertRaises(ValidationError):
            validate_days(0)
            validate_days(8)

    def test_slug(self):
        with self.assertRaises(ValidationError):
            validate_slug(None)
            validate_slug("")

    @mock.patch("shhh.api.utils.pwned_password")
    def test_strength(self, mock_pwned):
        with self.assertRaises(ValidationError):
            validate_strength("weak")
            validate_strength("Weak")
            validate_strength("Weak1")
            validate_strength("weak_but_long")
            validate_strength("weak_but_long_1")
            validate_strength("Weak_but_long")

            mock_pwned.return_value = 123
            validate_strength("Hello123")

            mock_pwned.side_effect = Exception
            validate_strength("Hello123j0e32hf")
