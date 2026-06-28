"""baseline reset schema

Revision ID: 20260626_baseline_reset_schema
Revises:
Create Date: 2026-06-26 19:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260626_baseline_reset_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline revision for the reset database."""

    pass


def downgrade() -> None:
    """Baseline revision cannot be meaningfully downgraded."""

    pass
