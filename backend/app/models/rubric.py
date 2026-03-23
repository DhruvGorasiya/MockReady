from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.user import UserRole


class RubricVersion(Base):
    __tablename__ = "rubric_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    # e.g. {"clarity": 0.2, "depth": 0.2, "structure": 0.2, "relevance": 0.2, "communication_quality": 0.2}  # noqa: E501
    weights: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sessions: Mapped[list["Session"]] = relationship(back_populates="rubric_version")  # noqa: F821
