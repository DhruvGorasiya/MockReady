"""
Tests for POST /api/v1/auth/register, POST /api/v1/auth/login, and GET /api/v1/auth/me.

Service layer is mocked so no real DB or JWT is needed.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.v1 import auth as auth_router_module
from app.main import app
from app.models.user import User, UserRole
from app.schemas.auth import TokenResponse, UserResponse


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def _make_user_response() -> UserResponse:
    return UserResponse(
        id=uuid4(),
        email="candidate@example.com",
        role=UserRole.candidate,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _make_token_response() -> TokenResponse:
    return TokenResponse(access_token="test.jwt.token")


# ---------------------------------------------------------------------------
# POST /api/v1/auth/register
# ---------------------------------------------------------------------------

def test_register_returns_201(client):
    user_response = _make_user_response()

    with patch(
        "app.api.v1.auth.auth_service.register_user",
        new=AsyncMock(return_value=user_response),
    ):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "candidate@example.com", "password": "Secure1pass"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "candidate@example.com"
    assert data["role"] == "candidate"
    assert "id" in data


def test_register_409_duplicate_email(client):
    with patch(
        "app.api.v1.auth.auth_service.register_user",
        new=AsyncMock(side_effect=HTTPException(status_code=409, detail="Email already registered.")),
    ):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "taken@example.com", "password": "Secure1pass"},
        )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_register_422_password_too_short(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "candidate@example.com", "password": "Ab1"},
    )
    assert response.status_code == 422


def test_register_422_password_missing_uppercase(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "candidate@example.com", "password": "alllower1"},
    )
    assert response.status_code == 422


def test_register_422_password_missing_digit(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "candidate@example.com", "password": "NoDigitsHere"},
    )
    assert response.status_code == 422


def test_register_422_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "Secure1pass"},
    )
    assert response.status_code == 422


def test_register_422_missing_fields(client):
    response = client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422


def test_register_503_on_db_error(client):
    with patch(
        "app.api.v1.auth.auth_service.register_user",
        new=AsyncMock(side_effect=RuntimeError("db connection lost")),
    ):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "candidate@example.com", "password": "Secure1pass"},
        )

    assert response.status_code == 503


# ---------------------------------------------------------------------------
# POST /api/v1/auth/login
# ---------------------------------------------------------------------------

def test_login_returns_200_with_token(client):
    token_response = _make_token_response()

    with patch(
        "app.api.v1.auth.auth_service.login_user",
        new=AsyncMock(return_value=token_response),
    ):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "candidate@example.com", "password": "Secure1pass"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "test.jwt.token"
    assert data["token_type"] == "bearer"


def test_login_401_wrong_password(client):
    with patch(
        "app.api.v1.auth.auth_service.login_user",
        new=AsyncMock(side_effect=HTTPException(status_code=401, detail="Invalid email or password.")),
    ):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "candidate@example.com", "password": "WrongPass1"},
        )

    assert response.status_code == 401


def test_login_401_unknown_email(client):
    with patch(
        "app.api.v1.auth.auth_service.login_user",
        new=AsyncMock(side_effect=HTTPException(status_code=401, detail="Invalid email or password.")),
    ):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@example.com", "password": "Secure1pass"},
        )

    assert response.status_code == 401


def test_login_422_invalid_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "Secure1pass"},
    )
    assert response.status_code == 422


def test_login_422_missing_fields(client):
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422


def test_login_503_on_db_error(client):
    with patch(
        "app.api.v1.auth.auth_service.login_user",
        new=AsyncMock(side_effect=RuntimeError("db connection lost")),
    ):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "candidate@example.com", "password": "Secure1pass"},
        )

    assert response.status_code == 503


# ---------------------------------------------------------------------------
# GET /api/v1/auth/me
# ---------------------------------------------------------------------------


def _make_user(role: UserRole = UserRole.candidate) -> User:
    u = User()
    u.id = uuid4()
    u.email = f"{role.value}@test.com"
    u.role = role
    u.password_hash = "x"
    u.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return u


def _make_auth_app(current_user: User | None) -> FastAPI:
    """Build a FastAPI app with the auth router mounted and get_current_user overridden.

    Pass current_user=None to leave auth unmocked (used to assert the endpoint is
    dependency-guarded).
    """
    from app.core.db import get_db
    from app.core.security import get_current_user

    test_app = FastAPI()
    test_app.include_router(auth_router_module.router, prefix="/api/v1")

    async def _override_db():
        yield AsyncMock()

    test_app.dependency_overrides[get_db] = _override_db

    if current_user is not None:
        async def _override_auth():
            return current_user

        test_app.dependency_overrides[get_current_user] = _override_auth

    return test_app


def test_me_returns_current_user_for_candidate():
    user = _make_user(UserRole.candidate)
    client = TestClient(_make_auth_app(user))

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["email"] == user.email
    assert data["role"] == "candidate"
    assert "created_at" in data


def test_me_returns_coach_role_for_coach_user():
    user = _make_user(UserRole.coach)
    client = TestClient(_make_auth_app(user))

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["role"] == "coach"


def test_me_returns_401_without_auth():
    test_app = _make_auth_app(current_user=None)
    client = TestClient(test_app, raise_server_exceptions=False)

    with patch("app.core.security.settings") as mock_settings:
        mock_settings.dev_bypass_auth = False
        response = client.get("/api/v1/auth/me")

    assert response.status_code == 401