import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScoredBy(str, enum.Enum):
    ai = "ai"
    coach = "coach"


class EvaluationScore(Base):
    __tablename__ = "evaluation_scores"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_question_id: Mapped[UUID] = mapped_column(
        ForeignKey("session_questions.id"), nullable=False
    )
    scored_by: Mapped[ScoredBy] = mapped_column(Enum(ScoredBy), nullable=False)
    coach_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Dimension scores: integers 1-10
    clarity: Mapped[int] = mapped_column(Integer, nullable=False)
    depth: Mapped[int] = mapped_column(Integer, nullable=False)
    structure: Mapped[int] = mapped_column(Integer, nullable=False)
    relevance: Mapped[int] = mapped_column(Integer, nullable=False)
    communication_quality: Mapped[int] = mapped_column(Integer, nullable=False)

    composite_score: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)

    # Per-dimension reasoning (AI) or justification (coach)
    reasoning: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session_question: Mapped["SessionQuestion"] = relationship(back_populates="evaluation_scores")  # noqa: F821
