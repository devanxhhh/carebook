import pytest
from app.core.config import settings

if not settings.TEST_DATABASE_URL:
    raise RuntimeError(
        "Integration tests require PostgreSQL. Set TEST_DATABASE_URL in the "
        "environment or .env before running pytest."
    )
if not settings.TEST_DATABASE_URL.startswith(("postgresql://", "postgresql+")):
    raise RuntimeError(
        "Integration tests require PostgreSQL. TEST_DATABASE_URL must use "
        "a PostgreSQL connection URL."
    )

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.centre import DiagnosticCentre
from app.models.test import DiagnosticTest, CentreTest

engine = create_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_db():
    """Create schema once per test session, drop it at the end."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _truncate_all(connection):
    """Truncate all tables to reset state between tests."""
    tables = ", ".join(
        f'"{t.name}"' for t in reversed(Base.metadata.sorted_tables)
    )
    if tables:
        connection.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
        connection.commit()


@pytest.fixture(scope="function")
def db_session(setup_db):
    """
    Provides a fresh database session for each test.
    After each test, all tables are truncated to ensure isolation.
    This pattern correctly handles the fact that the service layer calls
    db.commit() directly — real commits are made and then wiped clean afterwards.
    """
    session = TestingSessionLocal()
    yield session
    session.close()
    # Clean up between tests
    with engine.connect() as conn:
        _truncate_all(conn)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_db]


@pytest.fixture
def normal_user(db_session):
    user = User(
        name="Test User",
        email="user@test.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.USER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    user = User(
        name="Admin User",
        email="admin@test.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_user_token(client, normal_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "password123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def admin_user_token(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "password123"},
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def setup_catalogue(db_session):
    centre = DiagnosticCentre(name="Test Centre", location="City Center", is_active=True)
    db_session.add(centre)

    test = DiagnosticTest(name="Blood Test", code="BT01", category="Blood", is_active=True)
    db_session.add(test)
    db_session.commit()

    ct = CentreTest(centre_id=centre.id, test_id=test.id, price=500.0, is_available=True)
    db_session.add(ct)
    db_session.commit()

    return {"centre": centre, "test": test, "centre_test": ct}
