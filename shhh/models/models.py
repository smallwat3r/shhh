# pylint: disable=unused-argument, no-self-use, missing-function-docstring
from datetime import datetime

from sqlalchemy.ext.declarative import declared_attr

from shhh.extensions import db


class Base:
    """Base model class."""

    id = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return cls.__name__.lower()


class _DateTime(db.TypeDecorator):
    """Format datetime object before passing off to the database."""

    impl = db.DateTime

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value


class Entries(db.Model, Base):
    """Database model for secret entries."""

    encrypted_text = db.Column(db.LargeBinary)
    date_created = db.Column(_DateTime)
    date_expires = db.Column(_DateTime, nullable=True)
    slug_link = db.Column(db.String(20), unique=True, nullable=False)
    tries = db.Column(db.Integer, default=5)
    haveibeenpwned = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Entry {self.slug_link}>"
