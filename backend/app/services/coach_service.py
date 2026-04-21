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
)
from app.services.session_service import (
    _authoritative_score,
    _build_question_result,
    _composite_for_session,
    _compute_weighted_composite,
)


async def submit_coach_score(
    db: AsyncSession,
    session_id: UUID,
    question_id: UUID,
    coach_id: UUID,
    scores: dict,
    justification: str | None,
) -> QuestionResult:
    """Persist a coach override score for a session question. Returns the updated QuestionResult."""
    stmt = (
        select(SessionQuestion)
        .where(
            SessionQuestion.id == question_id,
            SessionQuestion.session_id == session_id,
        )
        .options(
            selectinload(SessionQuestion.evaluation_scores),
            selectinload(SessionQuestion.session).selectinload(Session.rubric_version),
        )
    )
    result = await db.execute(stmt)
    sq = result.scalar_one_or_none()

    if sq is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    already_coach_scored = any(s.scored_by == ScoredBy.coach for s in sq.evaluation_scores)
    if already_coach_scored:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Coach score already submitted for this question",
        )

    dim_scores = DimensionScores(**scores)
    rubric_weights = sq.session.rubric_version.weights if sq.session.rubric_version else None
    composite = _compute_weighted_composite(dim_scores, rubric_weights)

    coach_score = EvaluationScore(
        session_question_id=sq.id,
        scored_by=ScoredBy.coach,
        coach_id=coach_id,
        clarity=dim_scores.clarity,
        depth=dim_scores.depth,
        structure=dim_scores.structure,
        relevance=dim_scores.relevance,
        communication_quality=dim_scores.communication_quality,
        composite_score=composite,
        justification=justification,
    )
    db.add(coach_score)

    # Append to the in-memory list so _build_question_result sees both scores
    sq.evaluation_scores.append(coach_score)

    # Mark session as reviewed
    sq.session.status = SessionStatus.reviewed

    await db.commit()

    return _build_question_result(sq)


async def get_session_detail_as_coach(
    db: AsyncSession, session_id: UUID
) -> SessionDetail:
    """Return full session detail for coach review.

    Unlike the candidate-facing version, the query is NOT scoped by
    candidate_id: coaches audit sessions belonging to other users. Route-layer
    role enforcement is the only gate.
    """
    stmt = (
        select(Session)
        .where(Session.id == session_id)
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


async def list_sessions_for_review(db: AsyncSession) -> SessionHistoryResponse:
    """Return all completed sessions that have no coach scores yet, newest first."""
    stmt = (
        select(Session)
        .where(Session.status == SessionStatus.completed)
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
