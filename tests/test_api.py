from datetime import datetime, timedelta
from http import HTTPStatus
from urllib.parse import urlparse

import pytest
from flask import url_for

from shhh.api.responses import Message, Status
from shhh.domain import model
from shhh.extensions import db


@pytest.fixture
def post_payload() -> dict[str, str]:
    return {"secret": "message", "passphrase": "Hello123", "expire": "3d"}


@pytest.fixture
def secret(post_payload) -> model.Secret:
    secret = model.Secret.encrypt(message=post_payload["secret"],
                                  passphrase=post_payload["passphrase"],
                                  expire_code=post_payload["expire"])
    db.session.add(secret)
    db.session.commit()
    return secret


def test_api_post_create_secret(app, post_payload):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(url_for("api.secret"), json=post_payload)
    data = response.get_json()
    assert response.status_code == HTTPStatus.CREATED

    # ensure all the keys are present in the response
    for field in ("status", "details", "external_id", "link", "expires_on"):
        assert field in data["response"].keys()

    # test status is correct
    assert data["response"]["status"] == Status.CREATED

    # test expiry date is correct
    assert data["response"]["expires_on"].split(" at ")[0] == (
        datetime.now() + timedelta(days=3)).strftime("%B %d, %Y")

    # test the generated link uses the custom SHHH_HOST variable
    hostname = urlparse(data["response"]["link"]).netloc
    assert hostname == "test.test"

    # test the record is persisted
    external_id = data["response"]["external_id"]
    record = db.session.query(model.Secret).filter(
        model.Secret.has_external_id(external_id)).one_or_none()
    assert record is not None


def test_api_post_wrong_expire_value(app, post_payload):
    post_payload["expire"] = "12m"
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(url_for("api.secret"), json=post_payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.get_json()
    assert data["response"]["status"] == Status.ERROR
    assert data["response"]["details"] == ("Must be one of: 10m, 30m, 1h, "
                                           "3h, 6h, 1d, 2d, 3d, 5d, 7d.")


@pytest.mark.parametrize("field", ("passphrase", "secret"))
def test_api_post_missing_required_field(app, post_payload, field):
    post_payload.pop(field)
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(url_for("api.secret"), json=post_payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.get_json()
    assert data["response"]["status"] == Status.ERROR
    assert data["response"]["details"] == "Missing data for required field."


@pytest.mark.parametrize("passphrase",
                         ("hello", "Hello", "Helloooo", "h3lloooo"))
def test_api_post_weak_passphrase(app, post_payload, passphrase):
    post_payload["passphrase"] = passphrase
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(url_for("api.secret"), json=post_payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.get_json()
    assert data["response"]["status"] == Status.ERROR
    assert data["response"]["details"] == (
        "Sorry, your passphrase is too weak. It needs minimum 8 "
        "characters, with 1 number and 1 uppercase.")


def test_api_get_wrong_passphrase(app, secret):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(
            url_for("api.secret",
                    external_id=secret.external_id,
                    passphrase="wrong!"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.get_json()
    assert data["response"]["status"] == Status.INVALID
    assert data["response"]["msg"] == Message.INVALID.format(
        remaining=secret.tries)


def test_api_get_exceeded_tries(app, secret):
    # set only one try to remain on secret
    secret.tries = 1
    db.session.commit()

    external_id = secret.external_id

    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(
            url_for("api.secret",
                    external_id=secret.external_id,
                    passphrase="wrong!"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.get_json()
    assert data["response"]["status"] == Status.INVALID
    assert data["response"]["msg"] == Message.EXCEEDED

    secret = db.session.query(model.Secret).filter(
        model.Secret.has_external_id(external_id)).one_or_none()

    # the secret should have been deleted
    assert secret is None


def test_api_message_expired(app):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(
            url_for("api.secret",
                    external_id="123456",
                    passphrase="Hello123"))
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.get_json()
    assert data["response"]["status"] == Status.EXPIRED
    assert data["response"]["msg"] == Message.NOT_FOUND


def test_api_read_secret(app, secret, post_payload):
    external_id = secret.external_id
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(
            url_for("api.secret",
                    external_id=external_id,
                    passphrase=post_payload["passphrase"]))
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data["response"]["status"] == Status.SUCCESS
    assert data["response"]["msg"] == post_payload["secret"]

    secret = db.session.query(model.Secret).filter(
        model.Secret.has_external_id(external_id)).one_or_none()

    # the secret should have been deleted
    assert secret is None
