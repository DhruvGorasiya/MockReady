from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.evaluation_score import EvaluationScore, ScoredBy
from app.models.question import SessionQuestion
from app.models.session import Session, SessionStatus
from app.schemas.session import (
    DimensionScores,
    QuestionResult,
    SessionDetail,
    SessionHistoryResponse,
    SessionSummary,
    TrendPoint,
    TrendResponse,
)


def _authoritative_score(scores: list[EvaluationScore]) -> EvaluationScore | None:
    """Return the coach score if one exists, otherwise the AI score."""
    coach = next((s for s in scores if s.scored_by == ScoredBy.coach), None)
    if coach:
        return coach
    return next((s for s in scores if s.scored_by == ScoredBy.ai), None)


def _composite_for_session(session: Session) -> float | None:
    """Average the authoritative composite scores across all questions in a session."""
    scores = [
        _authoritative_score(sq.evaluation_scores)
        for sq in session.questions
    ]
    valid = [float(s.composite_score) for s in scores if s is not None]
    if not valid:
        return None
    return round(sum(valid) / len(valid), 1)


def _dimension_scores_for(score: EvaluationScore) -> DimensionScores:
    return DimensionScores(
        clarity=score.clarity,
        depth=score.depth,
        structure=score.structure,
        relevance=score.relevance,
        communication_quality=score.communication_quality,
    )


def _avg_dimension_scores(scores: list[EvaluationScore]) -> DimensionScores | None:
    """Average the authoritative dimension scores across all questions in a session."""
    auth_scores = [_authoritative_score(sq_scores) for sq_scores in scores if sq_scores]
    valid = [s for s in auth_scores if s is not None]
    if not valid:
        return None
    return DimensionScores(
        clarity=round(sum(s.clarity for s in valid) / len(valid)),
        depth=round(sum(s.depth for s in valid) / len(valid)),
        structure=round(sum(s.structure for s in valid) / len(valid)),
        relevance=round(sum(s.relevance for s in valid) / len(valid)),
        communication_quality=round(sum(s.communication_quality for s in valid) / len(valid)),
    )


def _build_question_result(sq: SessionQuestion) -> QuestionResult:
    ai_score = next((s for s in sq.evaluation_scores if s.scored_by == ScoredBy.ai), None)
    coach_score = next((s for s in sq.evaluation_scores if s.scored_by == ScoredBy.coach), None)

    feedback: dict | None = None
    if ai_score and ai_score.reasoning:
        feedback = ai_score.reasoning

    return QuestionResult(
        id=sq.id,
        question_text=sq.question_text,
        candidate_answer=sq.candidate_answer,
        order_index=sq.order_index,
        ai_scores=_dimension_scores_for(ai_score) if ai_score else None,
        coach_scores=_dimension_scores_for(coach_score) if coach_score else None,
        feedback=feedback,
    )


async def list_sessions(db: AsyncSession, candidate_id: UUID) -> SessionHistoryResponse:
    """Return all completed/reviewed sessions for a candidate, newest first."""
    stmt = (
        select(Session)
        .where(
            Session.candidate_id == candidate_id,
            Session.status.in_([SessionStatus.completed, SessionStatus.reviewed]),
        )
        .options(
            selectinload(Session.questions).selectinload(SessionQuestion.evaluation_scores)
        )
        .order_by(Session.created_at.desc())
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    summaries = [
        SessionSummary(
            id=s.id,
            interview_type=s.interview_type,
            role=s.role,
            status=s.status,
            composite_score=_composite_for_session(s),
            created_at=s.created_at,
        )
        for s in sessions
    ]
    return SessionHistoryResponse(sessions=summaries, total=len(summaries))


async def get_session_detail(
    db: AsyncSession, session_id: UUID, candidate_id: UUID
) -> SessionDetail:
    """Return full session detail including per-question scores. Raises 404 if not found."""
    stmt = (
        select(Session)
        .where(Session.id == session_id, Session.candidate_id == candidate_id)
        .options(
            selectinload(Session.questions).selectinload(SessionQuestion.evaluation_scores)
        )
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    questions = sorted(
        [_build_question_result(sq) for sq in session.questions],
        key=lambda q: q.order_index,
    )
    return SessionDetail(
        id=session.id,
        interview_type=session.interview_type,
        role=session.role,
        status=session.status,
        composite_score=_composite_for_session(session),
        created_at=session.created_at,
        questions=questions,
    )


async def get_score_trends(
    db: AsyncSession, candidate_id: UUID, limit: int = 10
) -> TrendResponse:
    """Return the last `limit` completed/reviewed sessions sorted ascending for trend charts."""
    stmt = (
        select(Session)
        .where(
            Session.candidate_id == candidate_id,
            Session.status.in_([SessionStatus.completed, SessionStatus.reviewed]),
        )
        .options(
            selectinload(Session.questions).selectinload(SessionQuestion.evaluation_scores)
        )
        .order_by(Session.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    # Sort ascending so the chart reads left-to-right chronologically
    sessions = sorted(sessions, key=lambda s: s.created_at)

    points: list[TrendPoint] = []
    for s in sessions:
        composite = _composite_for_session(s)
        all_sq_scores = [sq.evaluation_scores for sq in s.questions]
        dim_scores = _avg_dimension_scores(all_sq_scores)

        # Skip sessions that have no scored questions
        if composite is None or dim_scores is None:
            continue

        points.append(
            TrendPoint(
                session_id=s.id,
                created_at=s.created_at,
                composite_score=composite,
                dimension_scores=dim_scores,
            )
        )

    return TrendResponse(points=points)
