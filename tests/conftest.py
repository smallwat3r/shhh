import pytest

from shhh.adapters import orm
from shhh.constants import EnvConfig
from shhh.entrypoint import create_app
from shhh.extensions import db


@pytest.fixture(scope="session", autouse=True)
def app():
    flask_app = create_app(env=EnvConfig.TESTING)
    db.app = flask_app

    with flask_app.app_context():
        orm.metadata.create_all(db.get_engine())

    yield flask_app

    with flask_app.app_context():
        orm.metadata.drop_all(db.get_engine())


@pytest.fixture(autouse=True)
def session(app):
    context = app.app_context()
    context.push()

    for table in reversed(orm.metadata.sorted_tables):
        db.session.execute(table.delete())

    yield

    db.session.rollback()
    context.pop()
