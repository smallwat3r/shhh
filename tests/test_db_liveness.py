import os
import unittest
from http import HTTPStatus

from flask import url_for

from shhh.entrypoint import create_app
from shhh.extensions import db


class TestDbLiveness(unittest.TestCase):
    """DB liveness testing."""

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
        for table in reversed(self.db.metadata.sorted_tables):
            self.db.session.execute(table.delete())

    def tearDown(self):
        self.db.session.rollback()
        self.app_context.pop()

    def test_db_liveness_retries(self):
        # Kill database connection by deleting the test sqlite local file
        sqlite_connection_file = self.app.config["SQLALCHEMY_DATABASE_URI"].replace(
            "sqlite:///", ""
        )
        os.remove(sqlite_connection_file)

        # Make a request
        payload = {
            "secret": "secret message",
            "passphrase": "heeHk3h3i0o",
            "haveibeenpwned": True,
        }
        with self.app.test_request_context(), self.client as c:
            response = c.post(url_for("api.secret"), json=payload)

        # Request returns 503
        self.assertEqual(response.status_code, HTTPStatus.SERVICE_UNAVAILABLE.value)


if __name__ == "__main__":
    unittest.main()
