"""
Tests for POST /api/v1/auth/register and POST /api/v1/auth/login route handlers.

Service layer is mocked so no real DB or JWT is needed.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import UserRole
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