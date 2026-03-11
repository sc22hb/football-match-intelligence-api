"""test fixtures and in-memory db setup for api tests."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.fixture import Fixture  # noqa: F401
from app.core.security import reset_rate_limiter_state
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    reset_rate_limiter_state()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        # Tests use a known API key for write endpoints.
        test_client.headers.update({"X-API-Key": "dev-api-key"})
        yield test_client

    reset_rate_limiter_state()
    app.dependency_overrides.clear()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
