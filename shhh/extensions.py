# All extensions are used as singletons and initialized in application factory.
import time
from typing import Any, Union

from flask import current_app as app
from flask_sqlalchemy import BaseQuery, Model, SQLAlchemy
from sqlalchemy.exc import OperationalError

from flask_apscheduler import APScheduler
from flask_assets import Environment


class DatabaseNotReachable(Exception):
    """Couldn't connect to database."""


class RetryingQuery(BaseQuery):
    """Retry query if database isn't reachable."""

    _retry_count = 5
    _retry_sleep_interval_sec = 0.9

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self):
        for _ in range(self._retry_count):
            try:
                return super().__iter__()
            except OperationalError as err:
                app.logger.warning("Retrying to reach database...")
                time.sleep(self._retry_sleep_interval_sec)

        app.logger.critical("Database couldn't be reached.")
        raise DatabaseNotReachable


class CRUDMixin(Model):
    """Add convenience methods for CRUD operations with SQLAlchemy."""

    query_class = RetryingQuery

    @classmethod
    def create(cls, **kwargs) -> Union[bool, Any]:
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit: bool = True, **kwargs) -> Union[bool, Any]:
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save() if commit else self

    def save(self, commit: bool = True) -> Union[bool, Any]:
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit: bool = True) -> Union[bool, Any]:
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


db = SQLAlchemy(model_class=CRUDMixin, query_class=RetryingQuery)
assets = Environment()
scheduler = APScheduler()
