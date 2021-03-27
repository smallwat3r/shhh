import re
import unittest
from unittest import mock

from marshmallow import ValidationError

from shhh.api.validators import Validator


class TestValidators(unittest.TestCase):
    """API parameter validation testing."""

    def test_secret(self):
        not_valid = (None, "", 151 * "*")
        with self.assertRaises(ValidationError):
            for s in not_valid:
                Validator.secret(s)

        self.assertIsNone(Validator.secret(30 * "*"))

    def test_passphrase(self):
        not_valid = (None, "")
        with self.assertRaises(ValidationError):
            for s in not_valid:
                Validator.passphrase(s)

    def test_days(self):
        not_valid = (-1, 0, 8, 10)
        with self.assertRaises(ValidationError):
            for d in not_valid:
                Validator.days(d)

        for d in range(1, 8):
            self.assertIsNone(Validator.days(d))

    def test_tries(self):
        not_valid = (-1, 0, 2, 11)
        with self.assertRaises(ValidationError):
            for t in not_valid:
                Validator.tries(t)

        for t in range(3, 11):
            self.assertIsNone(Validator.tries(t))

    def test_slug(self):
        not_valid = (None, "")
        with self.assertRaises(ValidationError):
            for s in not_valid:
                Validator.slug(s)

    def test_strength(self):
        not_valid = (
            "weak",
            "Weak",
            "Weak1",
            "weak_but_long",
            "weak_but_long_1",
            "Weak_but_long",
        )
        with self.assertRaises(ValidationError):
            for word in not_valid:
                Validator.strength(word)

        self.assertIsNone(Validator.strength("UPPERlower9211"))

    @mock.patch("shhh.api.services.pwned_password")
    def test_haveibeenpwned(self, mock_pwned):
        with self.assertRaises(ValidationError):
            mock_pwned.return_value = 123
            Validator.haveibeenpwned("Hello123")

            mock_pwned.side_effect = Exception
            Validator.haveibeenpwned("Hello123j0e32hf")

        mock_pwned.return_value = False
        self.assertIsNone(Validator.haveibeenpwned("cjHeW9ihf9u43f9u4b3"))
