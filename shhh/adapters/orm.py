from sqlalchemy.orm import registry

from shhh.constants import DEFAULT_READ_TRIES_VALUE
from shhh.domain import model
from shhh.extensions import db

metadata = db.MetaData()

secret = db.Table(
    "secret",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("encrypted_text", db.LargeBinary),
    db.Column("date_created", db.DateTime),
    db.Column("date_expires", db.DateTime),
    db.Column("external_id", db.String(20), nullable=False),
    db.Column("tries", db.Integer, default=DEFAULT_READ_TRIES_VALUE))


def start_mappers() -> None:
    mapper_reg = registry()
    mapper_reg.map_imperatively(model.Secret, secret)
