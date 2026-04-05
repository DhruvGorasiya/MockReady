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


class EvaluationReasoning(BaseModel):
    clarity: str | None = None
    depth: str | None = None
    structure: str | None = None
    relevance: str | None = None
    communication_quality: str | None = None


class QuestionResult(BaseModel):
    id: UUID
    question_text: str
    candidate_answer: str | None
    order_index: int
    ai_scores: DimensionScores | None
    coach_scores: DimensionScores | None
    # Per-dimension reasoning (AI) or justification (coach)
    feedback: EvaluationReasoning | None


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


class SessionCreateResponse(BaseModel):
    session_id: UUID
    status: SessionStatus
    interview_type: InterviewType
    created_at: datetime


# --- Session creation ---


class CreateSessionRequest(BaseModel):
    interview_type: InterviewType
    role: InterviewRole
    # Used by create_session_with_questions; ignored by the bare POST /sessions endpoint
    question_count: int = Field(default=3, ge=1, le=5)


class QuestionInSession(BaseModel):
    id: UUID
    question_text: str
    order_index: int


class SessionCreatedResponse(BaseModel):
    id: UUID
    interview_type: InterviewType
    role: InterviewRole
    status: SessionStatus
    questions: list[QuestionInSession]


# --- Answer submission ---


class SubmitAnswerRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=5000)


class DimensionFeedback(BaseModel):
    clarity: str
    depth: str
    structure: str
    relevance: str
    communication_quality: str


class AnswerFeedbackResponse(BaseModel):
    session_question_id: UUID
    ai_scores: DimensionScores
    composite_score: float
    feedback_summary: str
    dimension_feedback: DimensionFeedback
    improvement_suggestion: str
    is_session_complete: bool
