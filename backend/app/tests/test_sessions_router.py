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
    DimensionScores,
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

def test_get_history_requires_auth(client):
    # FastAPI HTTPBearer returns 401 (not 403) when Authorization header is absent
    response = client.get("/api/v1/sessions/history")
    assert response.status_code == 401


def test_get_trends_requires_auth(client):
    response = client.get("/api/v1/sessions/trends")
    assert response.status_code == 401


def test_get_session_detail_requires_auth(client):
    response = client.get(f"/api/v1/sessions/{uuid4()}")
    assert response.status_code == 401


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
