from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.session import InterviewRole, InterviewType, SessionStatus


class DimensionScores(BaseModel):
    clarity: int = Field(..., ge=1, le=10)
    depth: int = Field(..., ge=1, le=10)
    structure: int = Field(..., ge=1, le=10)
    relevance: int = Field(..., ge=1, le=10)
    communication_quality: int = Field(..., ge=1, le=10)


class QuestionResult(BaseModel):
    id: UUID
    question_text: str
    candidate_answer: str | None
    order_index: int
    ai_scores: DimensionScores | None
    coach_scores: DimensionScores | None
    # Per-dimension reasoning (AI) or justification (coach)
    feedback: dict | None


class SessionSummary(BaseModel):
    id: UUID
    interview_type: InterviewType
    role: InterviewRole
    status: SessionStatus
    # Authoritative composite: coach score when present, else AI score
    composite_score: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionDetail(SessionSummary):
    questions: list[QuestionResult]


class SessionHistoryResponse(BaseModel):
    sessions: list[SessionSummary]
    total: int


class TrendPoint(BaseModel):
    session_id: UUID
    created_at: datetime
    composite_score: float
    dimension_scores: DimensionScores


class TrendResponse(BaseModel):
    points: list[TrendPoint]
