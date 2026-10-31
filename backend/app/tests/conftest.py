from collections.abc import Generator
from typing import Dict
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.services.auth_service import create_user_session
from app.utils.seed import seed_database

# Use in-memory SQLite with StaticPool so all connections share the same memory instance
TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all 23 database tables and seed initial roles, permissions, and demo users."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a transactional database session for an individual test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient configured with test database session dependency override."""
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_auth_headers(db_session: Session) -> Dict[str, str]:
    """Authentication header bearer token for System Administrator."""
    admin = db_session.query(User).filter_by(email="admin@brightloop.io").first()
    access_token, _, _ = create_user_session(db_session, admin)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def sales_auth_headers(db_session: Session) -> Dict[str, str]:
    """Authentication header bearer token for Sales Representative."""
    sales = db_session.query(User).filter_by(email="sales@brightloop.io").first()
    access_token, _, _ = create_user_session(db_session, sales)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def finance_auth_headers(db_session: Session) -> Dict[str, str]:
    """Authentication header bearer token for Finance Manager."""
    finance = db_session.query(User).filter_by(email="finance@brightloop.io").first()
    access_token, _, _ = create_user_session(db_session, finance)
    return {"Authorization": f"Bearer {access_token}"}

