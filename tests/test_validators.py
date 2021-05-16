import unittest
from unittest import mock

from marshmallow import ValidationError

from shhh.api.validators import Validator
from shhh.entrypoint import create_app


class TestValidators(unittest.TestCase):
    """API parameter validation testing."""

    def test_secret(self):
        # We need the app context as we need to access the app config
        app = create_app(env="testing")
        app_context = app.app_context()
        app_context.push()

        not_valid = (None, "", 251 * "*")
        for s in not_valid:
            with self.assertRaises(ValidationError):
                Validator.secret(s)

        self.assertIsNone(Validator.secret(30 * "*"))

    def test_passphrase(self):
        not_valid = (None, "")
        for s in not_valid:
            with self.assertRaises(ValidationError):
                Validator.passphrase(s)

    def test_days(self):
        not_valid = (-1, 0, 8, 10)
        for d in not_valid:
            with self.assertRaises(ValidationError):
                Validator.days(d)

        for d in range(1, 8):
            self.assertIsNone(Validator.days(d))

    def test_tries(self):
        not_valid = (-1, 0, 2, 11)
        for t in not_valid:
            with self.assertRaises(ValidationError):
                Validator.tries(t)

        for t in range(3, 11):
            self.assertIsNone(Validator.tries(t))

    def test_slug(self):
        not_valid = (None, "")
        for s in not_valid:
            with self.assertRaises(ValidationError):
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
        for word in not_valid:
            with self.assertRaises(ValidationError):
                Validator.strength(word)

        self.assertIsNone(Validator.strength("UPPERlower9211"))

    @mock.patch("shhh.api.validators.pwned_password")
    def test_haveibeenpwned(self, mock_pwned):
        with self.assertRaises(ValidationError):
            mock_pwned.return_value = 123
            Validator.haveibeenpwned("Hello123")

            mock_pwned.side_effect = Exception
            Validator.haveibeenpwned("Hello123j0e32hf")

        mock_pwned.return_value = False
        self.assertIsNone(Validator.haveibeenpwned("cjHeW9ihf9u43f9u4b3"))


if __name__ == "__main__":
    unittest.main()
