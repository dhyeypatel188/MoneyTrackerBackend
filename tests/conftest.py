"""
Pytest fixtures — each test gets a fresh in-memory SQLite DB via a shared connection.
We use a single connection with nested transactions so every test rolls back cleanly.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Override API key BEFORE importing app so middleware reads the correct value
from app.config import settings
settings.API_KEY = "test-api-key"
API_KEY_HEADERS = {"X-API-Key": "test-api-key"}

from app.main import app  # noqa: E402
from app.database import Base, get_db


@pytest.fixture(scope="function")
def client():
    # Use a file-based SQLite DB per test to avoid in-memory sharing issues
    engine = create_engine(
        "sqlite:///./test_expenses_temp.db",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    from app.dependencies import get_current_user
    from app import models

    def override_get_current_user():
        return models.User(id=1, username="testuser", is_active=True)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    # Clean up tables after each test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    import os
    try:
        os.remove("./test_expenses_temp.db")
    except FileNotFoundError:
        pass
