import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class InterviewType(str, enum.Enum):
    behavioral = "behavioral"
    technical = "technical"
    system_design = "system_design"
    mixed = "mixed"


class InterviewRole(str, enum.Enum):
    SWE = "SWE"
    PM = "PM"
    DS = "DS"


class SessionStatus(str, enum.Enum):
    created = "created"
    in_progress = "in_progress"
    completed = "completed"
    reviewed = "reviewed"
    abandoned = "abandoned"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    interview_type: Mapped[InterviewType] = mapped_column(Enum(InterviewType), nullable=False)
    role: Mapped[InterviewRole] = mapped_column(Enum(InterviewRole), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), nullable=False, default=SessionStatus.created
    )
    rubric_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("rubric_versions.id"), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    candidate: Mapped["User"] = relationship(back_populates="sessions")  # noqa: F821
    rubric_version: Mapped["RubricVersion | None"] = relationship(back_populates="sessions")  # noqa: F821
    questions: Mapped[list["SessionQuestion"]] = relationship(back_populates="session")  # noqa: F821
