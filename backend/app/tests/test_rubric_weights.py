"""
Tests for RubricVersion weight application in composite score calculation.
TDD red phase.
"""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.evaluation_score import EvaluationScore, ScoredBy
from app.models.question import SessionQuestion
from app.models.rubric import RubricVersion
from app.models.session import InterviewRole, InterviewType, Session, SessionStatus
from app.schemas.session import CreateSessionRequest
from app.services.session_service import _compute_weighted_composite, submit_answer
from app.schemas.session import DimensionScores

# ---------------------------------------------------------------------------
# Pure helper unit tests
# ---------------------------------------------------------------------------


def test_compute_weighted_composite_equal_weights():
    """With no weights, all dimensions contribute equally."""
    dims = DimensionScores(clarity=8, depth=6, structure=7, relevance=9, communication_quality=5)
    # equal weights → (8+6+7+9+5)/5 = 35/5 = 7.0
    result = _compute_weighted_composite(dims, weights=None)
    assert result == 7.0


def test_compute_weighted_composite_applies_custom_weights():
    """Custom weights produce a weighted average — only clarity counts."""
    dims = DimensionScores(clarity=10, depth=1, structure=1, relevance=1, communication_quality=1)
    weights = {
        "clarity": 1.0,
        "depth": 0.0,
        "structure": 0.0,
        "relevance": 0.0,
        "communication_quality": 0.0,
    }
    # only clarity contributes → 10.0
    result = _compute_weighted_composite(dims, weights=weights)
    assert result == 10.0


def test_compute_weighted_composite_partial_weights():
    """Weighted average computed correctly with non-uniform weights."""
    dims = DimensionScores(clarity=10, depth=10, structure=5, relevance=5, communication_quality=5)
    weights = {
        "clarity": 0.4,
        "depth": 0.4,
        "structure": 0.1,
        "relevance": 0.05,
        "communication_quality": 0.05,
    }
    # 4.0 + 4.0 + 0.5 + 0.25 + 0.25 = 9.0
    result = _compute_weighted_composite(dims, weights=weights)
    assert result == 9.0


# ---------------------------------------------------------------------------
# submit_answer integration: rubric weights applied to stored composite
# ---------------------------------------------------------------------------

_EVAL_OUTPUT = {
    "clarity": 10,
    "depth": 1,
    "structure": 1,
    "relevance": 1,
    "communication_quality": 1,
    "reasoning": {"clarity": "Perfect.", "depth": "Minimal.", "structure": "Minimal.", "relevance": "On topic.", "communication_quality": "OK."},
}

_FEEDBACK_OUTPUT = {
    "feedback_summary": "Good.",
    "dimension_feedback": {"clarity": "c", "depth": "d", "structure": "s", "relevance": "r", "communication_quality": "cq"},
    "improvement_suggestion": "Keep it up.",
}


def _make_session_with_rubric(rubric_weights):
    session = Session()
    session.id = uuid4()
    session.candidate_id = uuid4()
    session.interview_type = InterviewType.behavioral
    session.role = InterviewRole.SWE
    session.status = SessionStatus.in_progress
    session.started_at = None
    session.completed_at = None
    session.rubric_version_id = uuid4()

    rubric = RubricVersion()
    rubric.id = session.rubric_version_id
    rubric.weights = rubric_weights
    session.rubric_version = rubric

    sq = SessionQuestion()
    sq.id = uuid4()
    sq.session_id = session.id
    sq.question_id = uuid4()
    sq.question_text = "Tell me about a project."
    sq.order_index = 0
    sq.candidate_answer = None
    sq.submitted_at = None
    sq.evaluation_scores = []

    session.questions = [sq]
    return session, sq


def _make_session_no_rubric():
    session = Session()
    session.id = uuid4()
    session.candidate_id = uuid4()
    session.interview_type = InterviewType.behavioral
    session.role = InterviewRole.SWE
    session.status = SessionStatus.in_progress
    session.started_at = None
    session.completed_at = None
    session.rubric_version_id = None
    session.rubric_version = None

    sq = SessionQuestion()
    sq.id = uuid4()
    sq.session_id = session.id
    sq.question_id = uuid4()
    sq.question_text = "Tell me about a project."
    sq.order_index = 0
    sq.candidate_answer = None
    sq.submitted_at = None
    sq.evaluation_scores = []

    session.questions = [sq]
    return session, sq


def _db_for(session):
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = session
    db.execute = AsyncMock(return_value=result_mock)
    return db


@pytest.mark.asyncio
async def test_submit_answer_uses_rubric_weights_when_present():
    """When the session has a RubricVersion, composite_score uses those weights."""
    # clarity=1.0, all others=0 → composite should equal clarity score (10)
    weights = {"clarity": 1.0, "depth": 0.0, "structure": 0.0, "relevance": 0.0, "communication_quality": 0.0}
    session, sq = _make_session_with_rubric(weights)
    db = _db_for(session)

    with (
        patch("app.services.session_service.answer_evaluation.evaluate_answer") as mock_eval,
        patch("app.services.session_service.feedback_synthesis.synthesize_feedback") as mock_fb,
    ):
        mock_eval.return_value = _EVAL_OUTPUT
        mock_fb.return_value = _FEEDBACK_OUTPUT

        result = await submit_answer(
            db, session_id=session.id, question_id=sq.id,
            candidate_id=session.candidate_id, answer="My answer."
        )

    # clarity=10 × 1.0 + depth=1 × 0.0 + ... = 10.0
    assert result.composite_score == 10.0

    # Also verify the EvaluationScore added to DB has the weighted composite
    added_score = next(
        (call.args[0] for call in db.add.call_args_list if isinstance(call.args[0], EvaluationScore)),
        None,
    )
    assert added_score is not None
    assert float(added_score.composite_score) == 10.0


@pytest.mark.asyncio
async def test_submit_answer_uses_equal_weights_when_no_rubric():
    """When the session has no RubricVersion, composite_score uses equal weights."""
    session, sq = _make_session_no_rubric()
    db = _db_for(session)

    with (
        patch("app.services.session_service.answer_evaluation.evaluate_answer") as mock_eval,
        patch("app.services.session_service.feedback_synthesis.synthesize_feedback") as mock_fb,
    ):
        mock_eval.return_value = _EVAL_OUTPUT  # clarity=10, depth=1, structure=1, relevance=1, comm=1
        mock_fb.return_value = _FEEDBACK_OUTPUT

        result = await submit_answer(
            db, session_id=session.id, question_id=sq.id,
            candidate_id=session.candidate_id, answer="My answer."
        )

    # equal weights: (10+1+1+1+1)/5 = 14/5 = 2.8
    assert result.composite_score == 2.8
