"""baseline reset schema

Revision ID: 20260626_baseline_reset_schema
Revises:
Create Date: 2026-06-26 19:35:00.000000

"""
from typing import Sequence, Union

from alembic import op

from app.modules import import_model_modules
from app.shared.base_model import Base


revision: str = "20260626_baseline_reset_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Bootstrap the pre-academics schema for a fresh database."""

    import_model_modules()

    bind = op.get_bind()
    excluded_tables = {
        "student_subject_results",
        "report_cards",
        "report_card_subject_lines",
    }
    tables_to_create = [
        table
        for table in Base.metadata.sorted_tables
        if table.name not in excluded_tables
    ]

    Base.metadata.create_all(
        bind=bind,
        tables=tables_to_create,
        checkfirst=True,
    )


def downgrade() -> None:
    """Baseline revision cannot be meaningfully downgraded."""

    pass
