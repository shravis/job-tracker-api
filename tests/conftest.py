import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os


def _database_name(url: str) -> str:
    path = urlparse(url).path.lstrip("/")
    return path.split("?")[0]


def _is_test_database_url(url: str) -> bool:
    return "test" in _database_name(url).lower()


DEFAULT_TEST_DATABASE_URL = (
    "postgresql://jobtracker:jobtracker@localhost:5432/job_tracker_test"
)

test_url = os.environ.get("TEST_DATABASE_URL")
if test_url:
    os.environ["DATABASE_URL"] = test_url
elif "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = DEFAULT_TEST_DATABASE_URL

if not _is_test_database_url(os.environ["DATABASE_URL"]):
    raise RuntimeError(
        "Refusing to run tests against a non-test database "
        f"({_database_name(os.environ['DATABASE_URL'])!r}). "
        "Set TEST_DATABASE_URL to a database whose name contains 'test'."
    )

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db
from models import Base
from rate_limiter import reset_limiter_state

SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def client():
    reset_limiter_state()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    reset_limiter_state()
