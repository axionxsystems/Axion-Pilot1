"""
Shared pytest fixtures.

Environment is configured here *before* the app is imported so module-level
validation (e.g. the JWT SECRET_KEY length check) passes with test values.
"""
import os

# ── Test environment (must be set before importing app.*) ─────────────────────
os.environ.setdefault("ENV", "development")
os.environ.setdefault("SECRET_KEY", "0" * 64)  # satisfies the >=32 char check
os.environ.setdefault("DATABASE_URL", "")  # force the app onto the test DB below

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def _engine():
    """In-memory SQLite shared across connections for the whole test session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Import models so metadata is fully populated, then create the schema.
    import app.models  # noqa: F401
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(_engine, db_session):
    """TestClient with the DB dependency overridden to the in-memory test DB."""
    from app.main import app
    from app.database import get_db

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
