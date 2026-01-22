from http import HTTPStatus
from unittest.mock import PropertyMock, patch

from flask import Flask, url_for


def test_create_route(app):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(url_for("web.create"))
    assert response.status_code == HTTPStatus.OK


def test_robots_dot_txt_route(app):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(url_for("web.robots_dot_txt"))
        response.close()  # avoid unclosed file warning
    assert response.status_code == HTTPStatus.OK


def test_robots_dot_txt_no_static_folder(app):
    with app.test_request_context(), app.test_client() as test_client:
        with patch.object(Flask,
                          "static_folder",
                          new_callable=PropertyMock,
                          return_value=None):
            response = test_client.get(url_for("web.robots_dot_txt"))
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_read_route(app):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(
            url_for("web.read", external_id="fK6YTEVO2bvOln7pHOFi"))
    assert response.status_code == HTTPStatus.OK


def test_created_route(app):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(
            url_for("web.created",
                    link="https://test.test/r/z6HNg2dCcvvaOXli1z3x",
                    expires_on="2020-05-01%20at%2022:28%20UTC"))
    assert response.status_code == HTTPStatus.OK


def test_created_route_redirect(app):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(
            url_for("web.created",
                    link="https://test.test/r/z6HNg2dCcvvaOXli1z3x"))
    assert response.status_code == HTTPStatus.FOUND

    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(
            url_for("web.created", expires_on="2020-05-01%20at%2022:28%20UTC"))
    assert response.status_code == HTTPStatus.FOUND


def test_route_not_found(app):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get("/notfound")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_hsts_header_on_secure_request(app):
    with app.test_request_context(), app.test_client() as test_client:
        with patch("shhh.entrypoint.request") as mock_request:
            mock_request.is_secure = True
            response = test_client.get(url_for("web.create"))
    assert response.status_code == HTTPStatus.OK
    assert response.headers.get("Strict-Transport-Security") == \
        "max-age=63072000; includeSubDomains"
