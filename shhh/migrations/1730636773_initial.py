"""initial

Revision ID: 1730636773
Revises: 
Create Date: 2024-11-03 12:26:13.593575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1730636773'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ('default',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('secret',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('encrypted_text', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_expires', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('external_id', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('tries', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='secret_pkey')
    )


def downgrade() -> None:
    op.drop_table('secret')
