import json
import re
import unittest
from datetime import datetime, timedelta
from http import HTTPStatus
from types import SimpleNamespace
from urllib.parse import urlparse

import responses
from flask import url_for

from shhh.entrypoint import create_app
from shhh.extensions import db, scheduler
from shhh.models import Entries
from shhh.scheduler import tasks


class Parse(SimpleNamespace):
    """Nested dicts to use dot notation for clarity in tests."""

    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)
        for k, v in dictionary.items():
            if isinstance(v, dict):
                self.__setattr__(k, Parse(v))
            else:
                self.__setattr__(k, v)


class TestApplication(unittest.TestCase):
    """Flask application testing."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(env="testing")
        cls.db = db
        cls.db.app = cls.app
        cls.db.create_all()
        cls.scheduler = scheduler
        cls.scheduler.app = cls.app

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_all()
        cls.scheduler.shutdown(wait=False)

    def setUp(self):
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        for table in reversed(self.db.metadata.sorted_tables):
            self.db.session.execute(table.delete())
        # Mock responses from haveibeenpwned.
        responses.add(
            responses.GET,
            re.compile(r"^(https:\/\/api\.pwnedpasswords\.com\/range\/836BA).*"),
            body=(
                "BDDC66080E01D52B8272AA9461C69EE0496:12145\n"  # Hello123
                "00d4f6e8fa6eecad2a3aa415eec418d38ec:2"
            ),
        )
        responses.add(
            responses.GET,
            re.compile(r"^(https:\/\/api\.pwnedpasswords\.com\/)(?!.*836BA).*"),
            body=(
                "BDDC66080E01D52B8272AA9461C69EE0496:12145\n"  # Hello123
                "00d4f6e8fa6eecad2a3aa415eec418d38ec:2"
            ),
        )

    def tearDown(self):
        self.db.session.rollback()
        self.app_context.pop()

    def test_scheduler_setup(self):
        jobs = self.scheduler.get_jobs()
        # Test named scheduled task.
        self.assertEqual(jobs[0].name, "delete_expired_links")

        # Test task will run before next minute.
        scheduled = jobs[0].next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        next_minute = (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
        self.assertTrue(scheduled <= next_minute)

    def test_scheduler_job(self):
        # Temporarily pause the scheduler.
        self.scheduler.pause_job("delete_expired_links")

        # Add a dummy secret in database with an expired expiry date.
        slug = "z6HNg2dCcvvaOXli1z3x"
        encrypted_text = (
            b"nKir73XhgyXxjwYyCG-QHQABhqCAAAAAAF6rPvPYX7OYFZRTzy"
            b"PdIwvdo2SFwAN0VXrfosL54nGHr0MN1YtyoNjx4t5Y6058lFvDH"
            b"zsnv_Q1KaGFL6adJgLLVreOZ9kt5HpwnEe_Lod5Or85Ig=="
        )
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expired_date = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") - timedelta(days=1)

        Entries.create(
            slug_link=slug,
            encrypted_text=encrypted_text,
            date_created=now,
            date_expires=expired_date,
        )

        # Run scheduler task.
        tasks.delete_expired_links()
        # Check that the secret has been deleted from the database.
        link = Entries.query.filter_by(slug_link=slug).first()
        self.assertIsNone(link)

        # Resume the scheduler.
        self.scheduler.resume_job("delete_expired_links")

    def test_repr_entry(self):
        slug = "z6HNg2dCcvvaOXli1z3x"
        encrypted_text = (
            b"nKir73XhgyXxjwYyCG-QHQABhqCAAAAAAF6rPvPYX7OYFZRTzy"
            b"PdIwvdo2SFwAN0VXrfosL54nGHr0MN1YtyoNjx4t5Y6058lFvDH"
            b"zsnv_Q1KaGFL6adJgLLVreOZ9kt5HpwnEe_Lod5Or85Ig=="
        )
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expired_date = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") - timedelta(days=1)

        entry = Entries.create(
            slug_link=slug,
            encrypted_text=encrypted_text,
            date_created=now,
            date_expires=expired_date,
        )

        self.assertEqual(repr(entry), f"<Entry {slug}>")

    def test_views(self):
        with self.app.test_request_context(), self.client as c:
            # 200
            self.assertEqual(c.get(url_for("views.create")).status_code, HTTPStatus.OK.value)

            r = c.get("/robots.txt")
            r.close()  # avoids unclosed file warning.
            self.assertEqual(r.status_code, HTTPStatus.OK.value)

            self.assertEqual(
                c.get(url_for("views.read", slug="fK6YTEVO2bvOln7pHOFi")).status_code,
                HTTPStatus.OK.value,
            )
            self.assertEqual(
                c.get(
                    f"{url_for('views.created')}?link=https://shhh-encrypt.herokuapp.com/r/"
                    "z6HNg2dCcvvaOXli1z3x&expires_on=2020-05-01%20"
                    "at%2022:28%20UTC"
                ).status_code,
                HTTPStatus.OK.value,
            )

            # 302
            self.assertEqual(
                c.get(f"{url_for('views.created')}?link=only").status_code, HTTPStatus.FOUND.value
            )
            self.assertEqual(
                c.get(f"{url_for('views.created')}?expires_on=only").status_code,
                HTTPStatus.FOUND.value,
            )
            self.assertEqual(
                c.get(f"{url_for('views.created')}?link=only&other=only").status_code,
                HTTPStatus.FOUND.value,
            )

            # 404
            self.assertEqual(c.get("/read").status_code, HTTPStatus.NOT_FOUND.value)
            self.assertEqual(c.get("/donotexists").status_code, HTTPStatus.NOT_FOUND.value)

    @responses.activate
    def test_api_post_missing_all(self):
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret")).get_data())

        # Test response request status and error details.
        r = Parse(response)
        self.assertEqual(r.response.status, "error")

    @responses.activate
    def test_api_post_too_much_days(self):
        payload = {
            "secret": "secret message",
            "passphrase": "SuperSecret123",
            "days": 12,
        }
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # Test response request status and error details.
        r = Parse(response)
        self.assertEqual(r.response.status, "error")

    @responses.activate
    def test_api_post_wrong_formats(self):
        payload = {"secret": 1, "passphrase": 1, "days": "not an integer"}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # Test response request status and error details.
        r = Parse(response)
        self.assertEqual(r.response.status, "error")

    @responses.activate
    def test_api_post_missing_passphrase(self):
        payload = {"secret": "secret message"}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # Test response request status and error details.
        r = Parse(response)
        self.assertEqual(r.response.status, "error")

    @responses.activate
    def test_api_post_missing_secret(self):
        payload = {"passphrase": "SuperPassword123"}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # Test response request status and error details.
        r = Parse(response)
        self.assertEqual(r.response.status, "error")

    @responses.activate
    def test_api_post_passphrase_pwned(self):
        payload = {"passphrase": "Hello123"}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # Test response request status and error details.
        r = Parse(response)
        self.assertEqual(r.response.status, "error")

    def test_api_post_haveibeenpwned_not_reachable(self):
        payload = {
            "secret": "secret message",
            "passphrase": "Hello123",
            "haveibeenpwned": True,
        }
        with self.app.test_request_context(), self.client as c:
            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.GET,
                    re.compile(r"^(https:\/\/api\.pwnedpasswords\.com\/).*"),
                    body=Exception,
                )
                response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # haveibeenpwned wasn't reachable, but secret still created if it has
        # all mandatory requirements.
        r = Parse(response)
        self.assertEqual(r.response.status, "created")

    @responses.activate
    def test_api_post_dont_check_haveibeenpwned(self):
        payload = {
            "secret": "secret message",
            "passphrase": "Hello123",  # This passphrase has been pwned in the mock
            "haveibeenpwned": False,
        }

        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # Secret created without check from haveibeenpwned.
        r = Parse(response)
        self.assertEqual(r.response.status, "created")

    @responses.activate
    def test_api_post_check_haveibeenpwned_success(self):
        payload = {
            "secret": "secret message",
            "passphrase": "heeHk3h3i0o",
            "haveibeenpwned": True,
        }

        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # Secret created with check from haveibeenpwned.
        r = Parse(response)
        self.assertEqual(r.response.status, "created")

    @responses.activate
    def test_api_post_check_haveibeenpwned_failed(self):
        payload = {
            "secret": "secret message",
            "passphrase": "Hello123",  # This passphrase has been pwned in the mock
            "haveibeenpwned": True,
        }

        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        # Secret not created.
        r = Parse(response)
        self.assertEqual(r.response.status, "error")

    @responses.activate
    def test_api_post_weak_passphrase(self):
        # Weak passphrase.
        payload = {"secret": "secret message", "passphrase": "weak"}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        r = Parse(response)
        self.assertEqual(r.response.status, "error")

        # Long but all lowercase and no numbers.
        payload = {"secret": "secret message", "passphrase": "weak_but_long_passphrase"}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        r = Parse(response)
        self.assertEqual(r.response.status, "error")

        # Uppercase, lowercase, numbers, but too short.
        payload = {"secret": "secret message", "passphrase": "88AsA"}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        r = Parse(response)
        self.assertEqual(r.response.status, "error")

        # Long with numbers, but no uppercase.
        payload = {"secret": "secret message", "passphrase": "long_with_number_123"}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        r = Parse(response)
        self.assertEqual(r.response.status, "error")

    @responses.activate
    def test_api_post_created(self):
        payload = {"secret": "secret message", "passphrase": "PhduiGUI12d", "days": 3}
        with self.app.test_request_context(), self.client as c:
            response = json.loads(c.post(url_for("api.secret"), json=payload).get_data())

        r = Parse(response)

        # Test secret has been created and expiricy date is correct.
        self.assertEqual(r.response.status, "created")
        self.assertEqual(
            r.response.expires_on.split(" ")[0],
            (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        )

        # Test the link generated is using the test SHHH_HOST variable
        hostname = urlparse(r.response.link).netloc
        self.assertEqual(hostname, "test.test")

        # Test all fields in the response are correct.
        for field in ("status", "details", "slug", "link", "expires_on"):
            self.assertIn(field, r.response.__dict__.keys())

        # Test the slug link has been saved in the database.
        slug = r.response.slug
        link = Entries.query.filter_by(slug_link=slug).first()
        self.assertEqual(link.slug_link, slug)

    @responses.activate
    def test_api_get_wrong_passphrase(self):
        payload = {"secret": "secret message", "passphrase": "UGIUduigui12d"}
        with self.app.test_request_context(), self.client as c:
            post = json.loads(c.post(url_for("api.secret"), json=payload).get_data())
            response = json.loads(
                c.get(
                    f"{url_for('api.secret')}?slug={post['response']['slug']}&passphrase=wrong"
                ).get_data()
            )

        # Test passphrase is invalid.
        r = Parse(response)
        self.assertEqual(r.response.status, "invalid")

    @responses.activate
    def test_api_get_exceeded_tries(self):
        payload = {
            "secret": "secret message",
            "passphrase": "UGIUduigui12d",
            "tries": 3,
        }
        with self.app.test_request_context(), self.client as c:
            post = json.loads(c.post(url_for("api.secret"), json=payload).get_data())
            slug = post["response"]["slug"]

            for _ in range(payload["tries"]):
                response = json.loads(
                    c.get(
                        f"{url_for('api.secret')}?slug={post['response']['slug']}&passphrase=wrong"
                    ).get_data()
                )
                r = Parse(response)
                self.assertEqual(r.response.status, "invalid")

        # Secret has been deleted in database as number of tries has exceeded
        link = Entries.query.filter_by(slug_link=slug).first()
        self.assertIsNone(link)

    def test_api_get_wrong_slug(self):
        with self.app.test_request_context(), self.client as c:
            response = json.loads(
                c.get(f"{url_for('api.secret')}?slug=hello&passphrase=wrong").get_data()
            )

        # Test slug doesn't exists.
        r = Parse(response)
        self.assertEqual(r.response.status, "expired")

    @responses.activate
    def test_api_get_decrypt_secret(self):
        message, passphrase = "secret message", "dieh32u0hoHBI"
        payload = {"secret": message, "passphrase": passphrase}

        with self.app.test_request_context(), self.client as c:
            post = json.loads(c.post(url_for("api.secret"), json=payload).get_data())
            slug = post["response"]["slug"]
            response = json.loads(
                c.get(f"{url_for('api.secret')}?slug={slug}&passphrase={passphrase}").get_data()
            )

        r = Parse(response)
        # Test if status of the request is correct.
        self.assertEqual(r.response.status, "success")
        # Test if message has been decrypted correctly.
        self.assertEqual(r.response.msg, message)

        # Test if secret has been deleted in database.
        link = Entries.query.filter_by(slug_link=slug).first()
        self.assertIsNone(link)


if __name__ == "__main__":
    unittest.main()
