"""Test configuration and fixtures for pytest."""
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import get_session
from app.core.security import get_password_hash
from app.main import app
from app.models.base import Base
from app.models.token import PersonalAccessToken  # noqa: F401 – registers table
from app.models.user import User

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="engine")
def engine_fixture():
    """In-memory SQLite engine for tests."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_admin=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_admin")
def test_admin_fixture(session: Session) -> User:
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass123"),
        full_name="Admin User",
        is_active=True,
        is_admin=True,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


@pytest.fixture(name="user_token")
def user_token_fixture(client: TestClient, test_user: User) -> str:
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(name="admin_token")
def admin_token_fixture(client: TestClient, test_admin: User) -> str:
    response = client.post(
        "/api/auth/login",
        data={"username": test_admin.email, "password": "adminpass123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(user_token: str) -> dict:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}
