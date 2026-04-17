"""
Tests for the coach API router — route-level tests with auth mocked.
TDD red phase.
"""
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import coach as coach_router_module
from app.models.user import User, UserRole
from app.schemas.session import DimensionScores, QuestionResult, SessionHistoryResponse, SessionSummary
from app.models.session import InterviewType, InterviewRole, SessionStatus
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# App fixture with auth override
# ---------------------------------------------------------------------------


def _make_coach_user():
    u = User()
    u.id = uuid4()
    u.email = "coach@test.com"
    u.role = UserRole.coach
    u.password_hash = "x"
    u.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return u


def _make_candidate_user():
    u = User()
    u.id = uuid4()
    u.email = "candidate@test.com"
    u.role = UserRole.candidate
    u.password_hash = "x"
    u.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return u


def _make_app(current_user: User):
    from app.core.security import get_current_user
    from app.core.db import get_db

    app = FastAPI()
    app.include_router(coach_router_module.router, prefix="/api/v1/coach")

    async def _override_auth():
        return current_user

    async def _override_db():
        yield AsyncMock()

    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[get_db] = _override_db
    return app


_DIM_SCORES = DimensionScores(
    clarity=9, depth=8, structure=9, relevance=8, communication_quality=9
)

_QUESTION_RESULT = QuestionResult(
    id=uuid4(),
    question_text="Tell me about a project.",
    candidate_answer="I led a team...",
    order_index=0,
    ai_scores=_DIM_SCORES,
    coach_scores=_DIM_SCORES,
    feedback=None,
)

_SESSION_SUMMARY = SessionSummary(
    id=uuid4(),
    interview_type=InterviewType.behavioral,
    role=InterviewRole.SWE,
    status=SessionStatus.completed,
    composite_score=7.5,
    created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)

# ---------------------------------------------------------------------------
# POST /coach/sessions/{session_id}/questions/{question_id}/score
# ---------------------------------------------------------------------------


def test_coach_score_returns_200_for_coach_user():
    coach = _make_coach_user()
    app = _make_app(coach)
    client = TestClient(app)

    with patch("app.api.v1.coach.coach_service.submit_coach_score", new_callable=AsyncMock) as mock_svc:
        mock_svc.return_value = _QUESTION_RESULT

        resp = client.post(
            f"/api/v1/coach/sessions/{uuid4()}/questions/{uuid4()}/score",
            json={
                "scores": {"clarity": 9, "depth": 8, "structure": 9, "relevance": 8, "communication_quality": 9},
                "justification": "Stronger answer.",
            },
        )

    assert resp.status_code == 200
    assert resp.json()["coach_scores"]["clarity"] == 9


def test_coach_score_returns_403_for_candidate_user():
    candidate = _make_candidate_user()
    app = _make_app(candidate)
    client = TestClient(app)

    resp = client.post(
        f"/api/v1/coach/sessions/{uuid4()}/questions/{uuid4()}/score",
        json={
            "scores": {"clarity": 9, "depth": 8, "structure": 9, "relevance": 8, "communication_quality": 9},
        },
    )

    assert resp.status_code == 403


def test_coach_score_returns_401_without_auth():
    from app.core.security import get_current_user
    from app.core.db import get_db

    app = FastAPI()
    app.include_router(coach_router_module.router, prefix="/api/v1/coach")

    async def _override_db():
        yield AsyncMock()

    app.dependency_overrides[get_db] = _override_db
    client = TestClient(app, raise_server_exceptions=False)

    resp = client.post(
        f"/api/v1/coach/sessions/{uuid4()}/questions/{uuid4()}/score",
        json={"scores": {"clarity": 9, "depth": 8, "structure": 9, "relevance": 8, "communication_quality": 9}},
    )

    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /coach/sessions
# ---------------------------------------------------------------------------


def test_get_sessions_for_review_returns_200_for_coach():
    coach = _make_coach_user()
    app = _make_app(coach)
    client = TestClient(app)

    with patch("app.api.v1.coach.coach_service.list_sessions_for_review", new_callable=AsyncMock) as mock_svc:
        mock_svc.return_value = SessionHistoryResponse(sessions=[_SESSION_SUMMARY], total=1)

        resp = client.get("/api/v1/coach/sessions")

    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_get_sessions_for_review_returns_403_for_candidate():
    candidate = _make_candidate_user()
    app = _make_app(candidate)
    client = TestClient(app)

    resp = client.get("/api/v1/coach/sessions")

    assert resp.status_code == 403
