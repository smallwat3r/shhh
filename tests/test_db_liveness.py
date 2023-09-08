from http import HTTPStatus
from unittest import mock

from sqlalchemy.exc import OperationalError

from flask import url_for


@mock.patch("shhh.liveness._perform_db_connectivity_query",
            side_effect=OperationalError(None, None, None))
def test_db_liveness_cannot_be_reached(mock_perform_dummy_db_query,
                                       app,
                                       caplog):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(url_for("api.secret"),
                                    json={
                                        "secret": "secret message",
                                        "passphrase": "Hello123"
                                    })

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE  # 503
    assert ("Could not reach the database, something is wrong "
            "with the database connection") in caplog.text


@mock.patch("shhh.liveness._check_table_exists", return_value=False)
def test_db_liveness_table_does_not_exists(mock_check_table_exists,
                                           app,
                                           caplog):
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(url_for("api.secret"),
                                    json={
                                        "secret": "secret message",
                                        "passphrase": "Hello123"
                                    })

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE  # 503
    assert ("Could not query required table 'secret', make sure it "
            "has been created on the database") in caplog.text
