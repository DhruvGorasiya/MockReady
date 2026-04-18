"""
Tests for GET /api/v1/sessions/* route handlers — TDD red phase.

Auth and service layer are both mocked so no real DB or JWT is needed.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.session import InterviewRole, InterviewType, SessionStatus
from app.models.user import User, UserRole
from app.schemas.session import (
    AnswerFeedbackResponse,
    DimensionFeedback,
    DimensionScores,
    SessionCreatedResponse,
    SessionDetail,
    SessionHistoryResponse,
    SessionSummary,
    TrendPoint,
    TrendResponse,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_user(role: UserRole = UserRole.candidate) -> User:
    u = User()
    u.id = uuid4()
    u.email = "test@example.com"
    u.role = role
    u.password_hash = "hashed"
    u.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    u.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return u


def _make_summary(candidate_id=None) -> SessionSummary:
    return SessionSummary(
        id=uuid4(),
        interview_type=InterviewType.behavioral,
        role=InterviewRole.SWE,
        status=SessionStatus.completed,
        composite_score=7.5,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _make_detail(candidate_id=None) -> SessionDetail:
    return SessionDetail(
        id=uuid4(),
        interview_type=InterviewType.behavioral,
        role=InterviewRole.SWE,
        status=SessionStatus.completed,
        composite_score=7.5,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        questions=[],
    )


def _make_trend() -> TrendResponse:
    dim = DimensionScores(clarity=7, depth=7, structure=7, relevance=7, communication_quality=7)
    return TrendResponse(
        points=[
            TrendPoint(
                session_id=uuid4(),
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                composite_score=7.0,
                dimension_scores=dim,
            )
        ]
    )


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def unauthed_client():
    """Client with dev auth bypass disabled, simulating a real unauthenticated request."""
    with patch("app.core.security.settings") as mock_settings:
        mock_settings.dev_bypass_auth = False
        yield TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def authed_client():
    """Client with get_current_user dependency overridden to a candidate user."""
    from app.core.security import get_current_user

    user = _make_user(UserRole.candidate)

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app), user
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

def test_get_history_requires_auth(unauthed_client):
    assert unauthed_client.get("/api/v1/sessions/history").status_code == 401


def test_get_trends_requires_auth(unauthed_client):
    assert unauthed_client.get("/api/v1/sessions/trends").status_code == 401


def test_get_session_detail_requires_auth(unauthed_client):
    assert unauthed_client.get(f"/api/v1/sessions/{uuid4()}").status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v1/sessions/history
# ---------------------------------------------------------------------------

def test_get_history_returns_200_for_valid_candidate(authed_client):
    test_client, user = authed_client
    history = SessionHistoryResponse(sessions=[_make_summary()], total=1)

    with patch(
        "app.api.v1.sessions.session_service.list_sessions",
        new=AsyncMock(return_value=history),
    ):
        response = test_client.get("/api/v1/sessions/history")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["sessions"]) == 1


def test_get_history_empty_state_returns_empty_list(authed_client):
    test_client, user = authed_client
    empty = SessionHistoryResponse(sessions=[], total=0)

    with patch(
        "app.api.v1.sessions.session_service.list_sessions",
        new=AsyncMock(return_value=empty),
    ):
        response = test_client.get("/api/v1/sessions/history")

    assert response.status_code == 200
    data = response.json()
    assert data["sessions"] == []
    assert data["total"] == 0


# ---------------------------------------------------------------------------
# GET /api/v1/sessions/{session_id}
# ---------------------------------------------------------------------------

def test_get_session_detail_returns_200(authed_client):
    test_client, user = authed_client
    detail = _make_detail()

    with patch(
        "app.api.v1.sessions.session_service.get_session_detail",
        new=AsyncMock(return_value=detail),
    ):
        response = test_client.get(f"/api/v1/sessions/{detail.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(detail.id)


def test_get_session_detail_404_for_other_candidate(authed_client):
    test_client, user = authed_client

    with patch(
        "app.api.v1.sessions.session_service.get_session_detail",
        new=AsyncMock(side_effect=HTTPException(status_code=404, detail="Session not found")),
    ):
        response = test_client.get(f"/api/v1/sessions/{uuid4()}")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/sessions/trends
# ---------------------------------------------------------------------------

def test_get_trends_returns_trend_points(authed_client):
    test_client, user = authed_client
    trend = _make_trend()

    with patch(
        "app.api.v1.sessions.session_service.get_score_trends",
        new=AsyncMock(return_value=trend),
    ):
        response = test_client.get("/api/v1/sessions/trends")

    assert response.status_code == 200
    data = response.json()
    assert len(data["points"]) == 1
    assert data["points"][0]["composite_score"] == 7.0


def test_get_trends_empty_returns_empty_points(authed_client):
    test_client, user = authed_client
    empty_trend = TrendResponse(points=[])

    with patch(
        "app.api.v1.sessions.session_service.get_score_trends",
        new=AsyncMock(return_value=empty_trend),
    ):
        response = test_client.get("/api/v1/sessions/trends")

    assert response.status_code == 200
    assert response.json()["points"] == []


# ---------------------------------------------------------------------------
# GET /health (no auth required)
# ---------------------------------------------------------------------------

def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /api/v1/sessions
# ---------------------------------------------------------------------------


def test_create_session_requires_auth(unauthed_client):
    response = unauthed_client.post(
        "/api/v1/sessions",
        json={"interview_type": "behavioral", "role": "SWE"},
    )
    assert response.status_code == 401


def test_create_session_returns_422_for_invalid_interview_type(authed_client):
    test_client, _ = authed_client
    response = test_client.post(
        "/api/v1/sessions",
        json={"interview_type": "standup", "role": "SWE"},
    )
    assert response.status_code == 422


def test_create_session_returns_201(authed_client):
    test_client, user = authed_client
    session_response = SessionCreatedResponse(
        id=uuid4(),
        status=SessionStatus.in_progress,
        interview_type=InterviewType.behavioral,
        role=InterviewRole.SWE,
        questions=[],
    )

    with patch(
        "app.api.v1.sessions.session_service.create_session_with_questions",
        new=AsyncMock(return_value=session_response),
    ):
        response = test_client.post(
            "/api/v1/sessions",
            json={"interview_type": "behavioral", "role": "SWE"},
        )

    assert response.status_code == 201
    assert response.json()["status"] == "in_progress"


def test_create_session_returns_500_on_service_error(authed_client):
    test_client, _ = authed_client

    with patch(
        "app.api.v1.sessions.session_service.create_session_with_questions",
        new=AsyncMock(side_effect=RuntimeError("db exploded")),
    ):
        response = test_client.post(
            "/api/v1/sessions",
            json={"interview_type": "behavioral", "role": "SWE"},
        )

    assert response.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/v1/sessions/{session_id}/questions/{question_id}/answer
# ---------------------------------------------------------------------------

def _make_answer_response() -> AnswerFeedbackResponse:
    scores = DimensionScores(
        clarity=8, depth=7, structure=8, relevance=9, communication_quality=7
    )
    return AnswerFeedbackResponse(
        session_question_id=uuid4(),
        ai_scores=scores,
        composite_score=7.8,
        feedback_summary="Good answer overall.",
        dimension_feedback=DimensionFeedback(
            clarity="Clear explanation.",
            depth="Could go deeper.",
            structure="Well structured.",
            relevance="Directly relevant.",
            communication_quality="Communicated effectively.",
        ),
        improvement_suggestion="Add more concrete examples.",
        is_session_complete=False,
    )


def test_submit_answer_requires_auth(unauthed_client):
    url = f"/api/v1/sessions/{uuid4()}/questions/{uuid4()}/answer"
    response = unauthed_client.post(url, json={"answer": "My answer here."})
    assert response.status_code == 401


def test_submit_answer_returns_200(authed_client):
    test_client, _ = authed_client
    answer_response = _make_answer_response()

    with patch(
        "app.api.v1.sessions.session_service.submit_answer",
        new=AsyncMock(return_value=answer_response),
    ):
        response = test_client.post(
            f"/api/v1/sessions/{uuid4()}/questions/{uuid4()}/answer",
            json={"answer": "My answer here."},
        )

    assert response.status_code == 200
    assert response.json()["composite_score"] == 7.8


def test_submit_answer_404_session_not_found(authed_client):
    test_client, _ = authed_client

    with patch(
        "app.api.v1.sessions.session_service.submit_answer",
        new=AsyncMock(side_effect=HTTPException(status_code=404, detail="Session not found")),
    ):
        response = test_client.post(
            f"/api/v1/sessions/{uuid4()}/questions/{uuid4()}/answer",
            json={"answer": "My answer here."},
        )

    assert response.status_code == 404


def test_submit_answer_404_question_not_found(authed_client):
    test_client, _ = authed_client

    with patch(
        "app.api.v1.sessions.session_service.submit_answer",
        new=AsyncMock(side_effect=HTTPException(status_code=404, detail="Question not found")),
    ):
        response = test_client.post(
            f"/api/v1/sessions/{uuid4()}/questions/{uuid4()}/answer",
            json={"answer": "My answer here."},
        )

    assert response.status_code == 404


def test_submit_answer_409_already_answered(authed_client):
    test_client, _ = authed_client

    with patch(
        "app.api.v1.sessions.session_service.submit_answer",
        new=AsyncMock(side_effect=HTTPException(status_code=409, detail="Answer already submitted")),
    ):
        response = test_client.post(
            f"/api/v1/sessions/{uuid4()}/questions/{uuid4()}/answer",
            json={"answer": "My answer here."},
        )

    assert response.status_code == 409


def test_submit_answer_422_empty_answer(authed_client):
    test_client, _ = authed_client
    response = test_client.post(
        f"/api/v1/sessions/{uuid4()}/questions/{uuid4()}/answer",
        json={"answer": ""},
    )
    assert response.status_code == 422


def test_submit_answer_422_answer_too_long(authed_client):
    test_client, _ = authed_client
    response = test_client.post(
        f"/api/v1/sessions/{uuid4()}/questions/{uuid4()}/answer",
        json={"answer": "x" * 5001},
    )
    assert response.status_code == 422


def test_submit_answer_503_on_agent_failure(authed_client):
    test_client, _ = authed_client

    with patch(
        "app.api.v1.sessions.session_service.submit_answer",
        new=AsyncMock(side_effect=RuntimeError("agent timed out")),
    ):
        response = test_client.post(
            f"/api/v1/sessions/{uuid4()}/questions/{uuid4()}/answer",
            json={"answer": "My answer here."},
        )

    assert response.status_code == 503
