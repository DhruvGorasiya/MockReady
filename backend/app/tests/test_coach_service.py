"""
Tests for coach_service — submit_coach_score and list_sessions_for_review.
TDD red phase. All DB interaction mocked.
"""
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.evaluation_score import EvaluationScore, ScoredBy
from app.models.question import SessionQuestion
from app.models.session import InterviewRole, InterviewType, Session, SessionStatus
from app.services.coach_service import (
    get_session_detail_as_coach,
    list_sessions_for_review,
    submit_coach_score,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(candidate_id, status=SessionStatus.completed):
    s = Session()
    s.id = uuid4()
    s.candidate_id = candidate_id
    s.interview_type = InterviewType.behavioral
    s.role = InterviewRole.SWE
    s.status = status
    s.rubric_version_id = None
    s.rubric_version = None
    s.started_at = None
    s.completed_at = None
    s.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    s.questions = []
    return s


def _make_sq(session_id, has_ai_score=True, has_coach_score=False):
    sq = SessionQuestion()
    sq.id = uuid4()
    sq.session_id = session_id
    sq.question_id = uuid4()
    sq.question_text = "Tell me about a project."
    sq.order_index = 0
    sq.candidate_answer = "I led a team..."
    sq.submitted_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    sq.evaluation_scores = []

    if has_ai_score:
        ai = EvaluationScore()
        ai.id = uuid4()
        ai.session_question_id = sq.id
        ai.scored_by = ScoredBy.ai
        ai.coach_id = None
        ai.clarity = 7
        ai.depth = 7
        ai.structure = 7
        ai.relevance = 7
        ai.communication_quality = 7
        ai.composite_score = Decimal("7.0")
        ai.reasoning = {"clarity": "Good."}
        ai.justification = None
        ai.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        sq.evaluation_scores.append(ai)

    if has_coach_score:
        coach = EvaluationScore()
        coach.id = uuid4()
        coach.session_question_id = sq.id
        coach.scored_by = ScoredBy.coach
        coach.coach_id = uuid4()
        coach.clarity = 9
        coach.depth = 9
        coach.structure = 9
        coach.relevance = 9
        coach.communication_quality = 9
        coach.composite_score = Decimal("9.0")
        coach.reasoning = None
        coach.justification = "Better than AI judged."
        coach.created_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
        sq.evaluation_scores.append(coach)

    return sq


# ---------------------------------------------------------------------------
# submit_coach_score
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_submit_coach_score_creates_new_evaluation_score():
    """submit_coach_score must persist a new EvaluationScore with scored_by=coach."""
    session = _make_session(uuid4())
    sq = _make_sq(session.id, has_ai_score=True, has_coach_score=False)
    session.questions = [sq]

    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sq
    db.execute = AsyncMock(return_value=result_mock)

    coach_id = uuid4()
    scores = {"clarity": 9, "depth": 8, "structure": 9, "relevance": 8, "communication_quality": 9}

    result = await submit_coach_score(
        db,
        session_id=session.id,
        question_id=sq.id,
        coach_id=coach_id,
        scores=scores,
        justification="Stronger than AI judged.",
    )

    db.add.assert_called_once()
    added = db.add.call_args.args[0]
    assert isinstance(added, EvaluationScore)
    assert added.scored_by == ScoredBy.coach
    assert added.coach_id == coach_id
    assert added.clarity == 9
    assert added.justification == "Stronger than AI judged."


@pytest.mark.asyncio
async def test_submit_coach_score_returns_question_result():
    """submit_coach_score must return a QuestionResult with both ai_scores and coach_scores."""
    from app.schemas.session import QuestionResult

    session = _make_session(uuid4())
    sq = _make_sq(session.id, has_ai_score=True, has_coach_score=False)
    session.questions = [sq]

    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sq
    db.execute = AsyncMock(return_value=result_mock)

    scores = {"clarity": 9, "depth": 8, "structure": 9, "relevance": 8, "communication_quality": 9}

    result = await submit_coach_score(
        db,
        session_id=session.id,
        question_id=sq.id,
        coach_id=uuid4(),
        scores=scores,
        justification=None,
    )

    assert isinstance(result, QuestionResult)
    assert result.ai_scores is not None
    assert result.coach_scores is not None
    assert result.coach_scores.clarity == 9


@pytest.mark.asyncio
async def test_submit_coach_score_raises_404_when_question_not_found():
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(HTTPException) as exc_info:
        await submit_coach_score(
            db,
            session_id=uuid4(),
            question_id=uuid4(),
            coach_id=uuid4(),
            scores={"clarity": 8, "depth": 8, "structure": 8, "relevance": 8, "communication_quality": 8},
            justification=None,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_submit_coach_score_raises_409_when_already_scored():
    """If a coach score already exists, raise 409 Conflict."""
    session = _make_session(uuid4())
    sq = _make_sq(session.id, has_ai_score=True, has_coach_score=True)
    session.questions = [sq]

    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sq
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(HTTPException) as exc_info:
        await submit_coach_score(
            db,
            session_id=session.id,
            question_id=sq.id,
            coach_id=uuid4(),
            scores={"clarity": 9, "depth": 9, "structure": 9, "relevance": 9, "communication_quality": 9},
            justification=None,
        )

    assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# list_sessions_for_review
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_sessions_for_review_returns_only_completed_without_coach_scores():
    """Only completed sessions with no coach scores are returned."""
    candidate_id = uuid4()

    # session with AI scores only → needs review
    needs_review = _make_session(candidate_id, status=SessionStatus.completed)
    sq1 = _make_sq(needs_review.id, has_ai_score=True, has_coach_score=False)
    needs_review.questions = [sq1]

    # session already reviewed → skip
    already_reviewed = _make_session(candidate_id, status=SessionStatus.reviewed)
    sq2 = _make_sq(already_reviewed.id, has_ai_score=True, has_coach_score=True)
    already_reviewed.questions = [sq2]

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [needs_review]
    db.execute = AsyncMock(return_value=result_mock)

    from app.schemas.session import SessionHistoryResponse

    response = await list_sessions_for_review(db)

    assert isinstance(response, SessionHistoryResponse)
    assert response.total == 1
    assert response.sessions[0].id == needs_review.id


@pytest.mark.asyncio
async def test_list_sessions_for_review_returns_empty_when_all_reviewed():
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result_mock)

    from app.schemas.session import SessionHistoryResponse

    response = await list_sessions_for_review(db)

    assert response.total == 0
    assert response.sessions == []


@pytest.mark.asyncio
async def test_list_sessions_for_review_filters_to_completed_status():
    """Coach queue must filter WHERE status == 'completed'.

    Regression guard: the previous test mocks the DB result directly and
    therefore passes even if the WHERE clause is dropped or changed. This
    test introspects the compiled SQL so a refactor that loses the filter
    fails loudly.
    """
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result_mock)

    await list_sessions_for_review(db)

    db.execute.assert_awaited_once()
    stmt = db.execute.await_args.args[0]
    where_clause = str(stmt.whereclause.compile(compile_kwargs={"literal_binds": True}))
    assert "sessions.status" in where_clause
    assert "completed" in where_clause


# ---------------------------------------------------------------------------
# get_session_detail_as_coach
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_session_detail_as_coach_returns_detail_regardless_of_candidate():
    """Coach service returns any session; query MUST NOT be scoped by candidate_id."""
    from app.schemas.session import SessionDetail

    # Session belongs to a candidate that is NOT the coach
    session = _make_session(candidate_id=uuid4())
    sq = _make_sq(session.id, has_ai_score=True, has_coach_score=False)
    session.questions = [sq]

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = session
    db.execute = AsyncMock(return_value=result_mock)

    detail = await get_session_detail_as_coach(db, session_id=session.id)

    assert isinstance(detail, SessionDetail)
    assert detail.id == session.id
    assert len(detail.questions) == 1

    # Verify the SQL filter: session_id only, NOT candidate_id
    db.execute.assert_awaited_once()
    stmt = db.execute.await_args.args[0]
    where_clause = str(stmt.whereclause.compile(compile_kwargs={"literal_binds": False}))
    assert "sessions.id" in where_clause
    assert "candidate_id" not in where_clause


@pytest.mark.asyncio
async def test_get_session_detail_as_coach_raises_404_when_missing():
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(HTTPException) as exc_info:
        await get_session_detail_as_coach(db, session_id=uuid4())

    assert exc_info.value.status_code == 404
