"""add indexes

Revision ID: 1730637997
Revises: 1730636773
Create Date: 2024-11-03 12:46:37.418955

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1730637997'
down_revision: Union[str, None] = '1730636773'
branch_labels: Union[str, Sequence[str], None] = ()
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('date_expires_idx', 'secret', ['date_expires'], unique=False)
    op.create_index('external_id_idx', 'secret', ['external_id'], unique=False)


def downgrade() -> None:
    op.drop_index('external_id_idx', table_name='secret')
    op.drop_index('date_expires_idx', table_name='secret')
