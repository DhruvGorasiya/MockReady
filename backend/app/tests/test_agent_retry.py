"""
Tests for agent retry logic in session_service — TDD red phase.

The service must:
- Retry a failing agent call exactly once
- Return the result if the retry succeeds
- Raise HTTP 502 if both attempts fail
"""
from unittest.mock import AsyncMock, MagicMock, call, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.question import SessionQuestion
from app.models.session import InterviewRole, InterviewType, Session, SessionStatus
from app.schemas.session import CreateSessionRequest
from app.services.session_service import create_session_with_questions, submit_answer

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EVAL_OUTPUT = {
    "clarity": 7,
    "depth": 6,
    "structure": 8,
    "relevance": 7,
    "communication_quality": 7,
    "reasoning": {
        "clarity": "Clear explanation.",
        "depth": "Some depth.",
        "structure": "Good structure.",
        "relevance": "On topic.",
        "communication_quality": "Confident delivery.",
    },
}

_FEEDBACK_OUTPUT = {
    "feedback_summary": "Overall solid answer.",
    "dimension_feedback": {
        "clarity": "You opened clearly.",
        "depth": "Add more examples.",
        "structure": "Good signposting.",
        "relevance": "Stayed on topic.",
        "communication_quality": "Confident delivery.",
    },
    "improvement_suggestion": "Start with a one-line summary.",
}

_QUESTIONS_OUTPUT = [
    {"text": "Tell me about a time you led a project."},
    {"text": "Describe a technical challenge you solved."},
    {"text": "How would you design a URL shortener?"},
]


def _db_for_session_with_questions(session, questions):
    """Return a mock DB whose execute() returns a session with preloaded questions."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = session
    db.execute = AsyncMock(return_value=result_mock)
    return db


def _make_session_with_unanswered_question():
    session = Session()
    session.id = uuid4()
    session.candidate_id = uuid4()
    session.interview_type = InterviewType.behavioral
    session.role = InterviewRole.SWE
    session.status = SessionStatus.in_progress
    session.started_at = None
    session.completed_at = None

    sq = SessionQuestion()
    sq.id = uuid4()
    sq.session_id = session.id
    sq.question_id = uuid4()
    sq.question_text = "Tell me about a time you led a project."
    sq.order_index = 0
    sq.candidate_answer = None
    sq.submitted_at = None
    sq.evaluation_scores = []

    session.questions = [sq]
    return session, sq


# ---------------------------------------------------------------------------
# create_session_with_questions — question_generation retries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_session_retries_question_generation_on_first_failure():
    """If generate_questions fails once then succeeds, the session is still created."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    request = CreateSessionRequest(
        interview_type=InterviewType.behavioral,
        role=InterviewRole.SWE,
        question_count=3,
    )

    with patch("app.services.session_service.question_generation.generate_questions") as mock_gen:
        mock_gen.side_effect = [RuntimeError("timeout"), _QUESTIONS_OUTPUT]

        result = await create_session_with_questions(db, candidate_id=uuid4(), request=request)

    assert mock_gen.call_count == 2
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_session_raises_502_when_question_generation_fails_twice():
    """If generate_questions fails on both attempts, raise HTTP 502."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    request = CreateSessionRequest(
        interview_type=InterviewType.behavioral,
        role=InterviewRole.SWE,
        question_count=3,
    )

    with patch("app.services.session_service.question_generation.generate_questions") as mock_gen:
        mock_gen.side_effect = RuntimeError("timeout")

        with pytest.raises(HTTPException) as exc_info:
            await create_session_with_questions(db, candidate_id=uuid4(), request=request)

    assert exc_info.value.status_code == 502
    assert mock_gen.call_count == 2


# ---------------------------------------------------------------------------
# submit_answer — evaluate_answer retries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_submit_answer_retries_evaluate_answer_on_first_failure():
    """If evaluate_answer fails once then succeeds, the response is returned."""
    session, sq = _make_session_with_unanswered_question()
    db = _db_for_session_with_questions(session, session.questions)

    with (
        patch("app.services.session_service.answer_evaluation.evaluate_answer") as mock_eval,
        patch("app.services.session_service.feedback_synthesis.synthesize_feedback") as mock_fb,
    ):
        mock_eval.side_effect = [RuntimeError("timeout"), _EVAL_OUTPUT]
        mock_fb.return_value = _FEEDBACK_OUTPUT

        result = await submit_answer(
            db,
            session_id=session.id,
            question_id=sq.id,
            candidate_id=session.candidate_id,
            answer="My answer here.",
        )

    assert mock_eval.call_count == 2
    assert result.ai_scores.clarity == 7


@pytest.mark.asyncio
async def test_submit_answer_raises_502_when_evaluate_answer_fails_twice():
    """If evaluate_answer fails on both attempts, raise HTTP 502."""
    session, sq = _make_session_with_unanswered_question()
    db = _db_for_session_with_questions(session, session.questions)

    with (
        patch("app.services.session_service.answer_evaluation.evaluate_answer") as mock_eval,
        patch("app.services.session_service.feedback_synthesis.synthesize_feedback") as mock_fb,
    ):
        mock_eval.side_effect = RuntimeError("timeout")
        mock_fb.return_value = _FEEDBACK_OUTPUT

        with pytest.raises(HTTPException) as exc_info:
            await submit_answer(
                db,
                session_id=session.id,
                question_id=sq.id,
                candidate_id=session.candidate_id,
                answer="My answer here.",
            )

    assert exc_info.value.status_code == 502
    assert mock_eval.call_count == 2


# ---------------------------------------------------------------------------
# submit_answer — synthesize_feedback retries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_submit_answer_retries_synthesize_feedback_on_first_failure():
    """If synthesize_feedback fails once then succeeds, the response is returned."""
    session, sq = _make_session_with_unanswered_question()
    db = _db_for_session_with_questions(session, session.questions)

    with (
        patch("app.services.session_service.answer_evaluation.evaluate_answer") as mock_eval,
        patch("app.services.session_service.feedback_synthesis.synthesize_feedback") as mock_fb,
    ):
        mock_eval.return_value = _EVAL_OUTPUT
        mock_fb.side_effect = [RuntimeError("timeout"), _FEEDBACK_OUTPUT]

        result = await submit_answer(
            db,
            session_id=session.id,
            question_id=sq.id,
            candidate_id=session.candidate_id,
            answer="My answer here.",
        )

    assert mock_fb.call_count == 2
    assert result.feedback_summary == "Overall solid answer."


@pytest.mark.asyncio
async def test_submit_answer_raises_502_when_synthesize_feedback_fails_twice():
    """If synthesize_feedback fails on both attempts, raise HTTP 502."""
    session, sq = _make_session_with_unanswered_question()
    db = _db_for_session_with_questions(session, session.questions)

    with (
        patch("app.services.session_service.answer_evaluation.evaluate_answer") as mock_eval,
        patch("app.services.session_service.feedback_synthesis.synthesize_feedback") as mock_fb,
    ):
        mock_eval.return_value = _EVAL_OUTPUT
        mock_fb.side_effect = RuntimeError("timeout")

        with pytest.raises(HTTPException) as exc_info:
            await submit_answer(
                db,
                session_id=session.id,
                question_id=sq.id,
                candidate_id=session.candidate_id,
                answer="My answer here.",
            )

    assert exc_info.value.status_code == 502
    assert mock_fb.call_count == 2
