"""add auth identities table

Revision ID: 20260630_add_auth_identities
Revises: 20260630_staging_branch_baseline
Create Date: 2026-06-30 03:10:00.000000

"""

from typing import Sequence, Union

from alembic import op

from app.modules.auth_identity.models import AuthIdentity


revision: str = "20260630_add_auth_identities"
down_revision: Union[str, Sequence[str], None] = "20260630_staging_branch_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the auth identities table for existing staging databases."""

    AuthIdentity.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Drop the auth identities table."""

    AuthIdentity.__table__.drop(bind=op.get_bind(), checkfirst=True)
