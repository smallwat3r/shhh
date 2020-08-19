import re
import unittest
from unittest import mock

from marshmallow import ValidationError

from shhh.api.validators import (
    validate_days,
    validate_haveibeenpwned,
    validate_passphrase,
    validate_secret,
    validate_slug,
    validate_strength,
    validate_tries,
)


class TestValidators(unittest.TestCase):
    """API parameter validation testing."""

    def test_secret(self):
        not_valid = (None, "", 151 * "*")
        with self.assertRaises(ValidationError):
            for s in not_valid:
                validate_secret(s)

        self.assertIsNone(validate_secret(30 * "*"))

    def test_passphrase(self):
        with self.assertRaises(ValidationError):
            validate_passphrase(None)
            validate_passphrase("")

    def test_days(self):
        not_valid = (-1, 0, 8, 10)
        with self.assertRaises(ValidationError):
            for d in not_valid:
                validate_days(d)

        for d in range(1, 8):
            self.assertIsNone(validate_days(d))

    def test_tries(self):
        not_valid = (-1, 0, 2, 11)
        with self.assertRaises(ValidationError):
            for t in not_valid:
                validate_tries(t)

        for t in range(3, 11):
            self.assertIsNone(validate_tries(t))

    def test_slug(self):
        not_valid = (None, "")
        with self.assertRaises(ValidationError):
            for s in not_valid:
                validate_slug(s)

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
                validate_strength(word)

        self.assertIsNone(validate_strength("UPPERlower9211"))

    @mock.patch("shhh.api.services.pwned_password")
    def test_haveibeenpwned(self, mock_pwned):
        with self.assertRaises(ValidationError):
            mock_pwned.return_value = 123
            validate_haveibeenpwned("Hello123")

            mock_pwned.side_effect = Exception
            validate_haveibeenpwned("Hello123j0e32hf")

        mock_pwned.return_value = False
        self.assertIsNone(validate_haveibeenpwned("cjHeW9ihf9u43f9u4b3"))
