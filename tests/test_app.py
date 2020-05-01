import json
import os
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace

from shhh.entrypoint import create_app
from shhh.extensions import db
from shhh.models import Entries


class Parse(SimpleNamespace):
    """Nested dicts to use dot notation for clarity in tests."""

    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)
        for k, v in dictionary.items():
            self.__setattr__(k, Parse(v)) if isinstance(
                v, dict) else self.__setattr__(k, v)


def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())


class TestApplication(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(env="testing")
        cls.db = db
        cls.db.app = cls.app
        cls.db.create_all()

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_all()

    def setUp(self):
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        clean_db(self.db)

    def tearDown(self):
        self.db.session.rollback()
        self.app_context.pop()

    def test_views(self):
        with self.client as c:
            # 200
            self.assertEqual(c.get("/").status_code, 200)
            self.assertEqual(c.get("/robots.txt").status_code, 200)
            self.assertEqual(c.get("/r/fK6YTEVO2bvOln7pHOFi").status_code, 200)
            # yapf: disable
            self.assertEqual(
                c.get("/c?link=https://shhh-encrypt.herokuapp.com/r/"
                      "z6HNg2dCcvvaOXli1z3x&expires_on=2020-05-01%20"
                      "at%2022:28%20UTC").status_code, 200)
            # yapf: enable

            # 302
            self.assertEqual(c.get("/c?link=only").status_code, 302)
            self.assertEqual(c.get("/c?expires_on=only").status_code, 302)
            self.assertEqual(c.get("/c?link=only&other=only").status_code, 302)

            # 404
            self.assertEqual(c.get("/r").status_code, 404)
            self.assertEqual(c.get("/donotexists").status_code, 404)

    def test_api_post_missing_all(self):
        with self.client as c:
            response = json.loads(c.post("/api/c").get_data())
            r = Parse(response)

            # Test response request status and error details.
            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.secret, list)
            self.assertIsInstance(r.response.details.json.passphrase, list)

    def test_api_post_too_much_days(self):
        with self.client as c:
            payload = {
                "secret": "secret message",
                "passphrase": "SuperSecret123",
                "days": 12
            }
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            # Test response request status and error details.
            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.days, list)

    def test_api_post_wrong_formats(self):
        with self.client as c:
            payload = {"secret": 1, "passphrase": 1, "days": "not an integer"}
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            # Test response request status and error details.
            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.days, list)
            self.assertIsInstance(r.response.details.json.passphrase, list)
            self.assertIsInstance(r.response.details.json.secret, list)

    def test_api_post_missing_passphrase(self):
        with self.client as c:
            payload = {"secret": "secret message"}
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            # Test response request status and error details.
            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.passphrase, list)

    def test_api_post_missing_secret(self):
        with self.client as c:
            payload = {"passphrase": "SuperPassword123"}
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            # Test response request status and error details.
            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.secret, list)

    def test_api_post_weak_passphrase(self):
        with self.client as c:
            # Weak passphrase.
            payload = {"secret": "secret message", "passphrase": "weak"}
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.passphrase, list)

            # Long but all lowercase and no numbers.
            payload = {
                "secret": "secret message",
                "passphrase": "weak_but_long_passphrase"
            }
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.passphrase, list)

            # Uppercase, lowercase, numbers, but too short.
            payload = {"secret": "secret message", "passphrase": "88AsA"}
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.passphrase, list)

            # Long with numbers, but no uppercase.
            payload = {
                "secret": "secret message",
                "passphrase": "long_with_number_123"
            }
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            self.assertEqual(r.response.status, "error")
            self.assertIsInstance(r.response.details.json.passphrase, list)

    def test_api_post_created(self):
        with self.client as c:
            payload = {
                "secret": "secret message",
                "passphrase": "PhduiGUI12d",
                "days": 3
            }
            response = json.loads(c.post("/api/c", json=payload).get_data())
            r = Parse(response)

            # Test secret has been created and expiricy date is correct.
            self.assertEqual(r.response.status, "created")
            self.assertEqual(
                r.response.expires_on.split(" ")[0],
                (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"))

            # Test all fields in the response are correct.
            for field in ("status", "details", "slug", "link", "expires_on"):
                self.assertIn(field, r.response.__dict__.keys())

            # Test the slug link has been saved in the database.
            slug = r.response.slug
            link = self.db.session.query(Entries).filter_by(
                slug_link=slug).first()
            self.assertEqual(link.slug_link, slug)

    def test_api_get_wrong_passphrase(self):
        with self.client as c:
            payload = {
                "secret": "secret message", "passphrase": "UGIUduigui12d"
            }
            post = json.loads(c.post("/api/c", json=payload).get_data())
            p = Parse(post)

            response = json.loads(
                c.get(f"/api/r?slug={p.response.slug}&passphrase=wrong")
                .get_data())

            r = Parse(response)
            # Test passphrase is invalid.
            self.assertEqual(r.response.status, "invalid")

    def test_api_get_wrong_slug(self):
        with self.client as c:
            response = json.loads(
                c.get("/api/r?slug=hello&passphrase=wrong").get_data())
            r = Parse(response)

            # Test slug don't exists.
            self.assertEqual(r.response.status, "expired")

    def test_api_get_decrypt_secret(self):
        with self.client as c:
            message, passphrase = "secret message", "dieh32u0hoHBI"
            payload = {"secret": message, "passphrase": passphrase}
            post = json.loads(c.post("/api/c", json=payload).get_data())
            p = Parse(post)
            slug = p.response.slug

            response = json.loads(
                c.get(f"/api/r?slug={slug}&passphrase={passphrase}").get_data())
            r = Parse(response)

            # Test if status of the request is correct.
            self.assertEqual(r.response.status, "success")

            # Test if message has been decrypted correctly.
            self.assertEqual(r.response.msg, message)

            # Test if secret has been deleted in database.
            link = self.db.session.query(Entries).filter_by(
                slug_link=slug).first()
            self.assertIsNone(link)


if __name__ == "__main__":
    unittest.main()
