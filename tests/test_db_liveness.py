from http import HTTPStatus
from unittest import mock

from sqlalchemy.exc import OperationalError

from flask import url_for


@mock.patch("shhh.liveness._perform_dummy_db_query",
            side_effect=OperationalError(None, None, None))
def test_db_liveness_retries(mock_perform_dummy_db_query, app):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(url_for("api.secret"),
                                    json={
                                        "secret": "secret message",
                                        "passphrase": "Hello123"
                                    })

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE  # 503
