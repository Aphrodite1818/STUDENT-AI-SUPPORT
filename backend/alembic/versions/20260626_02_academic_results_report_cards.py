"""academic results report cards and parent relationship requests

Revision ID: 20260626_academic_results_report_cards
Revises: 20260626_baseline_reset_schema
Create Date: 2026-06-26 20:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260626_academic_results_report_cards"
down_revision: Union[str, Sequence[str], None] = "20260626_baseline_reset_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    academic_result_status = postgresql.ENUM(
        "draft",
        "submitted",
        "published",
        "locked",
        name="academic_result_status",
        schema="public",
    )
    report_card_status = postgresql.ENUM(
        "draft",
        "published",
        "archived",
        name="report_card_status",
        schema="public",
    )
    academic_result_status.create(op.get_bind(), checkfirst=True)
    report_card_status.create(op.get_bind(), checkfirst=True)

    op.execute("ALTER TYPE public.parentrelationship ADD VALUE IF NOT EXISTS 'sponsor'")
    op.add_column(
        "student_parent_link_requests",
        sa.Column(
            "relationship_type",
            sa.Enum(
                "father",
                "mother",
                "guardian",
                "sponsor",
                "other",
                name="parentrelationship",
                schema="public",
            ),
            server_default="guardian",
            nullable=False,
        ),
        schema="public",
    )

    op.create_table(
        "student_subject_results",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_subject_teacher_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("academic_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("academic_term_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("test_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("assessment_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("exam_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("total_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("grade", sa.String(10), nullable=False),
        sa.Column("remark", sa.String(100), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "submitted",
                "published",
                "locked",
                name="academic_result_status",
                schema="public",
            ),
            server_default="draft",
            nullable=False,
        ),
        sa.Column("recorded_by_actor_type", sa.String(50), nullable=False),
        sa.Column("recorded_by_actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["academic_session_id"], ["public.academic_sessions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["academic_term_id"], ["public.academic_terms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["class_id"], ["public.classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["class_subject_teacher_id"], ["public.class_subject_teachers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_id"], ["public.students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["public.subjects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["teacher_id"], ["public.teachers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["public.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "student_id",
            "class_subject_teacher_id",
            "academic_session_id",
            "academic_term_id",
            name="uq_student_subject_result_scope",
        ),
        schema="public",
    )
    op.create_index("ix_student_subject_results_tenant_student", "student_subject_results", ["tenant_id", "student_id"], schema="public")
    op.create_index("ix_student_subject_results_tenant_class", "student_subject_results", ["tenant_id", "class_id"], schema="public")
    op.create_index("ix_student_subject_results_tenant_teacher", "student_subject_results", ["tenant_id", "teacher_id"], schema="public")
    op.create_index("ix_student_subject_results_tenant_status", "student_subject_results", ["tenant_id", "status"], schema="public")

    op.create_table(
        "report_cards",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("academic_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("academic_term_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_score", sa.Numeric(7, 2), nullable=False),
        sa.Column("average_score", sa.Numeric(5, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "published", "archived", name="report_card_status", schema="public"),
            server_default="draft",
            nullable=False,
        ),
        sa.Column("generated_by_actor_type", sa.String(50), nullable=False),
        sa.Column("generated_by_actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["academic_session_id"], ["public.academic_sessions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["academic_term_id"], ["public.academic_terms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["class_id"], ["public.classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_id"], ["public.students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["public.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "student_id", "academic_session_id", "academic_term_id", name="uq_report_cards_student_period"),
        schema="public",
    )
    op.create_index("ix_report_cards_tenant_student", "report_cards", ["tenant_id", "student_id"], schema="public")
    op.create_index("ix_report_cards_tenant_status", "report_cards", ["tenant_id", "status"], schema="public")

    op.create_table(
        "report_card_subject_lines",
        sa.Column("report_card_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_subject_result_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_name", sa.String(100), nullable=False),
        sa.Column("subject_code", sa.String(30), nullable=True),
        sa.Column("teacher_name", sa.String(210), nullable=True),
        sa.Column("test_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("assessment_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("exam_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("total_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("grade", sa.String(10), nullable=False),
        sa.Column("remark", sa.String(100), nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["report_card_id"], ["public.report_cards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_subject_result_id"], ["public.student_subject_results.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subject_id"], ["public.subjects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["public.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "report_card_id", "subject_id", name="uq_report_card_lines_card_subject"),
        schema="public",
    )
    op.create_index("ix_report_card_lines_tenant_card", "report_card_subject_lines", ["tenant_id", "report_card_id"], schema="public")


def downgrade() -> None:
    op.drop_index("ix_report_card_lines_tenant_card", table_name="report_card_subject_lines", schema="public")
    op.drop_table("report_card_subject_lines", schema="public")
    op.drop_index("ix_report_cards_tenant_status", table_name="report_cards", schema="public")
    op.drop_index("ix_report_cards_tenant_student", table_name="report_cards", schema="public")
    op.drop_table("report_cards", schema="public")
    op.drop_index("ix_student_subject_results_tenant_status", table_name="student_subject_results", schema="public")
    op.drop_index("ix_student_subject_results_tenant_teacher", table_name="student_subject_results", schema="public")
    op.drop_index("ix_student_subject_results_tenant_class", table_name="student_subject_results", schema="public")
    op.drop_index("ix_student_subject_results_tenant_student", table_name="student_subject_results", schema="public")
    op.drop_table("student_subject_results", schema="public")
    op.drop_column("student_parent_link_requests", "relationship_type", schema="public")
    postgresql.ENUM(name="report_card_status", schema="public").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="academic_result_status", schema="public").drop(op.get_bind(), checkfirst=True)
