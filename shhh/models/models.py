from .. import db


class Slugs(db.Model):
    """Database models."""

    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)
    encrypted_text = db.Column(db.LargeBinary)
    date_created = db.Column(db.DateTime)
    date_expires = db.Column(db.DateTime, nullable=True)
    slug_link = db.Column(db.String(20),
                          index=True,
                          unique=True,
                          nullable=False)

    def __repr__(self):
        return f"<Slug {self.slug_link}>"
