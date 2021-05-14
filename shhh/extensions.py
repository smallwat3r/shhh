# All extensions are used as singletons and initialized in application factory.
from typing import Any, Union

from flask_apscheduler import APScheduler
from flask_assets import Environment
from flask_sqlalchemy import Model, SQLAlchemy


class CRUDMixin(Model):
    """Add convenience methods for CRUD operations with SQLAlchemy."""

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


db = SQLAlchemy(model_class=CRUDMixin)
assets = Environment()
scheduler = APScheduler()
