"""staging branch baseline schema

Revision ID: 20260630_staging_branch_baseline
Revises:
Create Date: 2026-06-30 02:40:00.000000

"""

from typing import Sequence, Union

from alembic import op

from app.modules import import_model_modules
from app.shared.base_model import Base


revision: str = "20260630_staging_branch_baseline"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the full staging schema from the current model metadata."""

    import_model_modules()
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Staging baseline is not intended to be downgraded."""

    pass
