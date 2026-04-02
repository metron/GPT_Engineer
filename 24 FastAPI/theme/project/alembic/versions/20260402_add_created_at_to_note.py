"""add created_at to note

Revision ID: bb6d9a0cb57d
Revises: c05dc6ebd736
Create Date: 2026-04-02 15:25:06.931873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb6d9a0cb57d'
down_revision: Union[str, Sequence[str], None] = 'c05dc6ebd736'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('note') as batch_op:
        batch_op.add_column(sa.Column(
            'created_at',
            sa.DateTime,
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False
        ))


def downgrade() -> None:
    with op.batch_alter_table('my_table') as batch_op:
        batch_op.drop_column('created_at')
