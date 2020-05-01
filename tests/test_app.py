import json
import os
import unittest
from datetime import datetime, timedelta
from unittest import mock

from shhh.entrypoint import create_app
from shhh.extensions import db
from shhh.models import Entries


def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())


class BaseTestCase(unittest.TestCase):
    db = None

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls.app = create_app(env="testing")
        cls.db = db
        cls.db.app = cls.app
        cls.db.create_all()

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_all()
        super(BaseTestCase, cls).tearDownClass()

    def setUp(self):
        super(BaseTestCase, self).setUp()

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        clean_db(self.db)

    def tearDown(self):
        self.db.session.rollback()
        self.app_context.pop()

        super(BaseTestCase, self).tearDown()

    def test_views(self):
        with self.app.test_client() as c:
            self.assertEqual(c.get("/").status_code, 200)
            self.assertEqual(c.get("/robots.txt").status_code, 200)
            self.assertEqual(c.get("/r/fK6YTEVO2bvOln7pHOFi").status_code, 200)
            # yapf: disable
            self.assertEqual(
                c.get("/c?link=https://shhh-encrypt.herokuapp.com/r/"
                      "z6HNg2dCcvvaOXli1z3x&expires_on=2020-05-01%20"
                      "at%2022:28%20UTC").status_code, 200)
            # yapf: enable

            self.assertEqual(c.get("/c?link=only").status_code, 302)
            self.assertEqual(c.get("/c?expires_on=only").status_code, 302)
            self.assertEqual(c.get("/c?link=only&other=only").status_code, 302)

            self.assertEqual(c.get("/r").status_code, 404)
            self.assertEqual(c.get("/donotexists").status_code, 404)

    def test_api_post_missing_all(self):
        with self.app.test_client() as c:
            response = json.loads(c.post("/api/c").get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("secret"), list)
            self.assertIsInstance(
                response["response"]["details"]["json"].get("passphrase"), list)

    def test_api_post_too_much_days(self):
        with self.app.test_client() as c:
            payload = {
                "secret": "secret message",
                "passphrase": "SuperSecret123",
                "days": 12
            }
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("days"), list)

    def test_api_post_wrong_formats(self):
        with self.app.test_client() as c:
            payload = {"secret": 1, "passphrase": 1, "days": "not an integer"}
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("days"), list)
            self.assertIsInstance(
                response["response"]["details"]["json"].get("passphrase"), list)
            self.assertIsInstance(
                response["response"]["details"]["json"].get("secret"), list)

    def test_api_post_missing_passphrase(self):
        with self.app.test_client() as c:
            payload = {"secret": "secret message", }
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("passphrase"), list)

    def test_api_post_missing_secret(self):
        with self.app.test_client() as c:
            payload = {"passphrase": "SuperPassword123", }
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("secret"), list)

    def test_api_post_weak_passphrase(self):
        with self.app.test_client() as c:
            payload = {"secret": "secret message", "passphrase": "weak"}
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("passphrase"), list)

            payload = {
                "secret": "secret message",
                "passphrase": "weak_but_long_passphrase"
            }
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("passphrase"), list)

            payload = {"secret": "secret message", "passphrase": "88AA"}
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("passphrase"), list)

            payload = {
                "secret": "secret message",
                "passphrase": "long_with_number_123"
            }
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "error")
            self.assertIsInstance(
                response["response"]["details"]["json"].get("passphrase"), list)

    def test_api_post_created(self):
        with self.app.test_client() as c:
            payload = {
                "secret": "secret message",
                "passphrase": "PhduiGUI12d",
                "days": 3
            }
            response = json.loads(c.post("/api/c", json=payload).get_data())

            self.assertEqual(response["response"]["status"], "created")
            self.assertEqual(response["response"]["expires_on"].split(" ")[0],
                             (datetime.now() +
                              timedelta(days=3)).strftime("%Y-%m-%d"))

            for field in ("status", "details", "slug", "link", "expires_on"):
                self.assertIn(field, response["response"].keys())

            slug = response["response"]["slug"]
            link = db.session.query(Entries).filter_by(slug_link=slug).first()
            self.assertEqual(link.slug_link, slug)

    def test_api_get_wrong_passphrase(self):
        with self.app.test_client() as c:
            payload = {
                "secret": "secret message", "passphrase": "UGIUduigui12d",
            }
            post = json.loads(c.post("/api/c", json=payload).get_data())
            slug = post["response"]["slug"]

            response = json.loads(
                c.get(f"/api/r?slug={slug}&passphrase=wrong").get_data())

            self.assertEqual(response["response"]["status"], "invalid")

    def test_api_get_wrong_slug(self):
        with self.app.test_client() as c:
            response = json.loads(
                c.get("/api/r?slug=hello&passphrase=wrong").get_data())

            self.assertEqual(response["response"]["status"], "expired")

    def test_api_get_decrypt_secret(self):
        with self.app.test_client() as c:
            message, passphrase = "secret message", "dieh32u0hoHBI"
            payload = {"secret": message, "passphrase": passphrase}
            post = json.loads(c.post("/api/c", json=payload).get_data())
            slug = post["response"]["slug"]

            response = json.loads(
                c.get(f"/api/r?slug={slug}&passphrase={passphrase}").get_data())

            self.assertEqual(response["response"]["status"], "success")
            self.assertEqual(response["response"]["msg"], message)
