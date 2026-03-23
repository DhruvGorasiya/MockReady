import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    interview_type: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty), nullable=False, default=Difficulty.medium
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SessionQuestion(Base):
    __tablename__ = "session_questions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    question_id: Mapped[UUID] = mapped_column(ForeignKey("questions.id"), nullable=False)
    # Snapshot of question text at session creation time — never re-fetched
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped["Session"] = relationship(back_populates="questions")  # noqa: F821
    evaluation_scores: Mapped[list["EvaluationScore"]] = relationship(  # noqa: F821
        back_populates="session_question"
    )
