"""initial schema

Revision ID: 64620107b2d5
Revises:
Create Date: 2026-03-22 22:24:56.745071

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "64620107b2d5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("candidate", "coach", "admin", name="userrole"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "rubric_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "role",
            sa.Enum("candidate", "coach", "admin", name="userrole"),
            nullable=False,
        ),
        sa.Column("weights", JSONB, nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "interview_type",
            sa.Enum("behavioral", "technical", "system_design", name="interviewtype"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("SWE", "PM", "DS", name="interviewrole"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "created", "in_progress", "completed", "reviewed", "abandoned",
                name="sessionstatus",
            ),
            nullable=False,
            server_default="created",
        ),
        sa.Column(
            "rubric_version_id",
            UUID(as_uuid=True),
            sa.ForeignKey("rubric_versions.id"),
            nullable=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "questions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("interview_type", sa.String(50), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column(
            "difficulty",
            sa.Enum("easy", "medium", "hard", name="difficulty"),
            nullable=False,
        ),
        sa.Column("tags", ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "session_questions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("question_id", UUID(as_uuid=True), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("order_index", sa.Integer, nullable=False),
        sa.Column("candidate_answer", sa.Text, nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "evaluation_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_question_id",
            UUID(as_uuid=True),
            sa.ForeignKey("session_questions.id"),
            nullable=False,
        ),
        sa.Column(
            "scored_by",
            sa.Enum("ai", "coach", name="scoredby"),
            nullable=False,
        ),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("clarity", sa.Integer, nullable=False),
        sa.Column("depth", sa.Integer, nullable=False),
        sa.Column("structure", sa.Integer, nullable=False),
        sa.Column("relevance", sa.Integer, nullable=False),
        sa.Column("communication_quality", sa.Integer, nullable=False),
        sa.Column("composite_score", sa.Numeric(4, 1), nullable=False),
        sa.Column("reasoning", JSONB, nullable=True),
        sa.Column("justification", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("evaluation_scores")
    op.drop_table("session_questions")
    op.drop_table("questions")
    op.drop_table("sessions")
    op.drop_table("rubric_versions")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS scoredby")
    op.execute("DROP TYPE IF EXISTS sessionstatus")
    op.execute("DROP TYPE IF EXISTS interviewrole")
    op.execute("DROP TYPE IF EXISTS interviewtype")
    op.execute("DROP TYPE IF EXISTS difficulty")
    op.execute("DROP TYPE IF EXISTS userrole")
