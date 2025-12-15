"""Added goals column to the practice_session table.

Revision ID: 63942a6aa5f4
Revises: 
Create Date: 2025-12-15 12:48:09.785288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63942a6aa5f4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "practice_session",
        sa.Column('goals', sa.String, nullable=True),
    )
    pass


def downgrade() -> None:
    op.drop_column(
        "practice_sesion",
        sa.Column("goals", sa.String),
    )
    pass
