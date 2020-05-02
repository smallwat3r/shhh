from datetime import datetime

from shhh.extensions import db


class _DateTime(db.TypeDecorator):
    impl = db.DateTime

    def process_bind_param(self, value, dialect): # pylint: disable=unused-argument, no-self-use
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value


class Entries(db.Model):
    """Database model for entry links."""

    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    encrypted_text = db.Column(db.LargeBinary)
    date_created = db.Column(_DateTime)
    date_expires = db.Column(_DateTime, nullable=True)
    slug_link = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"<Entry {self.slug_link}>"
