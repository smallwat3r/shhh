import re
import unittest
from unittest import mock

from marshmallow import ValidationError

from shhh.api.validators import (validate_days, validate_passphrase,
                                 validate_secret, validate_slug,
                                 validate_strength, validate_haveibeenpwned,
                                 validate_tries)


class TestValidators(unittest.TestCase):
    def test_secret(self):
        with self.assertRaises(ValidationError):
            validate_secret(None)
            validate_secret("")
            validate_secret(151 * "*")

        self.assertIsNone(validate_secret(30 * "*"))

    def test_passphrase(self):
        with self.assertRaises(ValidationError):
            validate_passphrase(None)
            validate_passphrase("")

    def test_days(self):
        with self.assertRaises(ValidationError):
            validate_days(-1)
            validate_days(0)
            validate_days(8)

        for d in range(1, 8):
            self.assertIsNone(validate_days(d))

    def test_tries(self):
        with self.assertRaises(ValidationError):
            validate_tries(-1)
            validate_tries(0)
            validate_tries(2)
            validate_tries(11)

        for t in range(3, 11):
            self.assertIsNone(validate_tries(t))

    def test_slug(self):
        with self.assertRaises(ValidationError):
            validate_slug(None)
            validate_slug("")

    def test_strength(self):
        with self.assertRaises(ValidationError):
            validate_strength("weak")
            validate_strength("Weak")
            validate_strength("Weak1")
            validate_strength("weak_but_long")
            validate_strength("weak_but_long_1")
            validate_strength("Weak_but_long")

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
