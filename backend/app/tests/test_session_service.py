"""
Tests for session_service.py — written before implementation (TDD red phase).

All DB interaction is mocked via AsyncMock so no real database is required.
The service is the unit under test; ORM models are constructed in-memory.
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
from app.schemas.session import SessionCreateResponse, SessionDetail, SessionHistoryResponse, TrendResponse
from app.services.session_service import create_session, get_score_trends, get_session_detail, list_sessions

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_session(candidate_id, status=SessionStatus.completed, created_at=None):
    s = Session()
    s.id = uuid4()
    s.candidate_id = candidate_id
    s.interview_type = InterviewType.behavioral
    s.role = InterviewRole.SWE
    s.status = status
    s.rubric_version_id = None
    s.started_at = None
    s.completed_at = None
    s.created_at = created_at or datetime(2026, 1, 1, tzinfo=timezone.utc)
    s.questions = []
    return s


def _make_ai_score(session_question_id, clarity=7, depth=7, structure=7, relevance=7, comm=7):
    e = EvaluationScore()
    e.id = uuid4()
    e.session_question_id = session_question_id
    e.scored_by = ScoredBy.ai
    e.coach_id = None
    e.clarity = clarity
    e.depth = depth
    e.structure = structure
    e.relevance = relevance
    e.communication_quality = comm
    e.composite_score = Decimal("7.0")
    e.reasoning = {"clarity": "Good clarity."}
    e.justification = None
    e.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return e


def _make_coach_score(  # noqa: PLR0913
    session_question_id, coach_id, clarity=9, depth=9, structure=9, relevance=9, comm=9
):
    e = EvaluationScore()
    e.id = uuid4()
    e.session_question_id = session_question_id
    e.scored_by = ScoredBy.coach
    e.coach_id = coach_id
    e.clarity = clarity
    e.depth = depth
    e.structure = structure
    e.relevance = relevance
    e.communication_quality = comm
    e.composite_score = Decimal("9.0")
    e.reasoning = None
    e.justification = "Stronger answer than AI judged."
    e.created_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
    return e


def _make_session_question(session_id, order_index=0):
    sq = SessionQuestion()
    sq.id = uuid4()
    sq.session_id = session_id
    sq.question_id = uuid4()
    sq.question_text = "Tell me about a time you led a project."
    sq.order_index = order_index
    sq.candidate_answer = "I led a team of five engineers..."
    sq.submitted_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    sq.evaluation_scores = []
    return sq


# ---------------------------------------------------------------------------
# list_sessions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_sessions_returns_empty_for_new_user():
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result_mock)

    response = await list_sessions(db, candidate_id=uuid4())

    assert isinstance(response, SessionHistoryResponse)
    assert response.sessions == []
    assert response.total == 0


@pytest.mark.asyncio
async def test_list_sessions_returns_sessions_for_candidate():
    candidate_id = uuid4()
    session = _make_session(candidate_id)
    sq = _make_session_question(session.id)
    ai_score = _make_ai_score(sq.id)
    sq.evaluation_scores = [ai_score]
    session.questions = [sq]

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [session]
    db.execute = AsyncMock(return_value=result_mock)

    response = await list_sessions(db, candidate_id=candidate_id)

    assert response.total == 1
    assert response.sessions[0].id == session.id
    assert response.sessions[0].composite_score == 7.0


@pytest.mark.asyncio
async def test_list_sessions_only_returns_completed_and_reviewed():
    candidate_id = uuid4()
    completed = _make_session(candidate_id, status=SessionStatus.completed)
    reviewed = _make_session(candidate_id, status=SessionStatus.reviewed)
    _make_session(candidate_id, status=SessionStatus.in_progress)
    _make_session(candidate_id, status=SessionStatus.abandoned)

    # Service filters by status — simulate DB returning only completed+reviewed
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [completed, reviewed]
    db.execute = AsyncMock(return_value=result_mock)

    response = await list_sessions(db, candidate_id=candidate_id)

    returned_statuses = {s.status for s in response.sessions}
    assert SessionStatus.in_progress not in returned_statuses
    assert SessionStatus.abandoned not in returned_statuses
    assert response.total == 2


@pytest.mark.asyncio
async def test_list_sessions_composite_score_is_none_when_no_scores():
    candidate_id = uuid4()
    session = _make_session(candidate_id)
    session.questions = []  # no questions answered yet

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [session]
    db.execute = AsyncMock(return_value=result_mock)

    response = await list_sessions(db, candidate_id=candidate_id)

    assert response.sessions[0].composite_score is None


# ---------------------------------------------------------------------------
# get_session_detail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_session_detail_returns_questions_and_scores():
    candidate_id = uuid4()
    session = _make_session(candidate_id)
    sq = _make_session_question(session.id, order_index=0)
    ai_score = _make_ai_score(sq.id)
    sq.evaluation_scores = [ai_score]
    session.questions = [sq]

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = session
    db.execute = AsyncMock(return_value=result_mock)

    detail = await get_session_detail(db, session_id=session.id, candidate_id=candidate_id)

    assert isinstance(detail, SessionDetail)
    assert len(detail.questions) == 1
    assert detail.questions[0].ai_scores.clarity == 7
    assert detail.questions[0].coach_scores is None


@pytest.mark.asyncio
async def test_get_session_detail_raises_404_when_not_found():
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(HTTPException) as exc_info:
        await get_session_detail(db, session_id=uuid4(), candidate_id=uuid4())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_session_detail_raises_404_for_wrong_candidate():
    real_owner_id = uuid4()
    other_candidate_id = uuid4()
    session = _make_session(real_owner_id)

    db = AsyncMock()
    result_mock = MagicMock()
    # DB query already filters by candidate_id — returns None for wrong user
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(HTTPException) as exc_info:
        await get_session_detail(db, session_id=session.id, candidate_id=other_candidate_id)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_session_detail_shows_both_ai_and_coach_scores():
    candidate_id = uuid4()
    coach_id = uuid4()
    session = _make_session(candidate_id)
    sq = _make_session_question(session.id)
    ai_score = _make_ai_score(sq.id, clarity=5)
    coach_score = _make_coach_score(sq.id, coach_id=coach_id, clarity=9)
    sq.evaluation_scores = [ai_score, coach_score]
    session.questions = [sq]

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = session
    db.execute = AsyncMock(return_value=result_mock)

    detail = await get_session_detail(db, session_id=session.id, candidate_id=candidate_id)

    q = detail.questions[0]
    assert q.ai_scores.clarity == 5
    assert q.coach_scores.clarity == 9


# ---------------------------------------------------------------------------
# get_score_trends
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_score_trends_returns_sorted_ascending_by_date():
    candidate_id = uuid4()
    earlier = _make_session(candidate_id, created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    later = _make_session(candidate_id, created_at=datetime(2026, 1, 5, tzinfo=timezone.utc))

    for s in [earlier, later]:
        sq = _make_session_question(s.id)
        sq.evaluation_scores = [_make_ai_score(sq.id)]
        s.questions = [sq]

    db = AsyncMock()
    result_mock = MagicMock()
    # DB returns them in descending order (latest first); service must sort asc
    result_mock.scalars.return_value.all.return_value = [later, earlier]
    db.execute = AsyncMock(return_value=result_mock)

    trend = await get_score_trends(db, candidate_id=candidate_id)

    assert isinstance(trend, TrendResponse)
    assert trend.points[0].created_at < trend.points[1].created_at


@pytest.mark.asyncio
async def test_get_score_trends_caps_at_last_10_sessions():
    candidate_id = uuid4()
    sessions = []
    for i in range(12):
        s = _make_session(candidate_id, created_at=datetime(2026, 1, i + 1, tzinfo=timezone.utc))
        sq = _make_session_question(s.id)
        sq.evaluation_scores = [_make_ai_score(sq.id)]
        s.questions = [sq]
        sessions.append(s)

    db = AsyncMock()
    result_mock = MagicMock()
    # Simulate DB already limiting to 10 (service passes limit=10 to query)
    result_mock.scalars.return_value.all.return_value = sessions[-10:]
    db.execute = AsyncMock(return_value=result_mock)

    trend = await get_score_trends(db, candidate_id=candidate_id, limit=10)

    assert len(trend.points) == 10


@pytest.mark.asyncio
async def test_get_score_trends_composite_uses_coach_score_when_present():
    candidate_id = uuid4()
    coach_id = uuid4()
    session = _make_session(candidate_id, created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    sq = _make_session_question(session.id)
    ai_score = _make_ai_score(sq.id)          # composite 7.0
    coach_score = _make_coach_score(sq.id, coach_id=coach_id)  # composite 9.0
    sq.evaluation_scores = [ai_score, coach_score]
    session.questions = [sq]

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [session]
    db.execute = AsyncMock(return_value=result_mock)

    trend = await get_score_trends(db, candidate_id=candidate_id)

    # Coach score is authoritative
    assert trend.points[0].composite_score == 9.0


@pytest.mark.asyncio
async def test_get_score_trends_skips_sessions_with_no_scores():
    candidate_id = uuid4()
    session_no_scores = _make_session(
        candidate_id, created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    session_no_scores.questions = []

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [session_no_scores]
    db.execute = AsyncMock(return_value=result_mock)

    trend = await get_score_trends(db, candidate_id=candidate_id)

    # Sessions with no scoreable questions are excluded from trend points
    assert len(trend.points) == 0


# ---------------------------------------------------------------------------
# create_session
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_session_returns_session_create_response():
    """create_session must return a SessionCreateResponse with the required fields."""
    user_id = uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    response = await create_session(db, user_id=user_id, interview_type=InterviewType.behavioral, role=InterviewRole.SWE)

    assert isinstance(response, SessionCreateResponse)


@pytest.mark.asyncio
async def test_create_session_response_has_required_fields():
    """SessionCreateResponse must expose session_id, status, interview_type, created_at."""
    user_id = uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    response = await create_session(db, user_id=user_id, interview_type=InterviewType.technical, role=InterviewRole.SWE)

    assert hasattr(response, "session_id")
    assert hasattr(response, "status")
    assert hasattr(response, "interview_type")
    assert hasattr(response, "created_at")


@pytest.mark.asyncio
async def test_create_session_sets_status_to_created():
    """Newly created sessions must have status=created."""
    user_id = uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    response = await create_session(db, user_id=user_id, interview_type=InterviewType.behavioral, role=InterviewRole.SWE)

    assert response.status == SessionStatus.created


@pytest.mark.asyncio
async def test_create_session_persists_interview_type():
    """The interview_type in the response must match the one passed in."""
    user_id = uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    response = await create_session(db, user_id=user_id, interview_type=InterviewType.technical, role=InterviewRole.SWE)

    assert response.interview_type == InterviewType.technical


@pytest.mark.asyncio
async def test_create_session_adds_session_to_db_and_commits():
    """create_session must call db.add and db.commit exactly once each."""
    user_id = uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    await create_session(db, user_id=user_id, interview_type=InterviewType.technical, role=InterviewRole.SWE)

    db.add.assert_called_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_session_session_id_is_uuid():
    """session_id in the response must be a valid UUID."""
    from uuid import UUID

    user_id = uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    response = await create_session(db, user_id=user_id, interview_type=InterviewType.behavioral, role=InterviewRole.SWE)

    assert isinstance(response.session_id, UUID)


@pytest.mark.asyncio
async def test_create_session_created_at_is_datetime():
    """created_at in the response must be a datetime instance."""
    user_id = uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    response = await create_session(db, user_id=user_id, interview_type=InterviewType.behavioral, role=InterviewRole.SWE)

    assert isinstance(response.created_at, datetime)
