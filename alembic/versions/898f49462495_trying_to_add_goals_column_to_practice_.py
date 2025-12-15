"""Trying to add goals column to practice_session table

Revision ID: 898f49462495
Revises: 63942a6aa5f4
Create Date: 2025-12-15 13:02:42.173677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '898f49462495'
down_revision: Union[str, Sequence[str], None] = '63942a6aa5f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "practice_session",
        sa.Column('goals', sa.String(), nullable=True),
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
