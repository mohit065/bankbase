import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db
from app.db.models import Base, Employee
from app.core.security import get_password_hash
from tests.factories import EmployeeFactory

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    EmployeeFactory._meta.sqlalchemy_session = session
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    yield session

    session.rollback()
    session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def admin_user(db_session) -> Employee:
    admin = EmployeeFactory(
        email="admin@example.com",
        role="admin",
        password_hash=get_password_hash("adminpass"),
    )
    db_session.commit()
    return admin

@pytest.fixture
def clerk_user(db_session) -> Employee:
    clerk = EmployeeFactory(
        email="clerk@example.com",
        role="clerk",
        password_hash=get_password_hash("clerkpass"),
    )
    db_session.commit()
    return clerk

@pytest.fixture
def get_auth_token(client):
    def _get_token(email: str, password: str):
        response = client.post(
            "/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200, f"Login failed for {email}: {response.text}"
        return response.json()["access_token"]
    return _get_token

@pytest.fixture
def admin_client(client, get_auth_token, admin_user):
    token = get_auth_token(admin_user.email, "adminpass")
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

@pytest.fixture
def non_admin_client(client, get_auth_token, clerk_user):
    token = get_auth_token(clerk_user.email, "clerkpass")
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

@pytest.fixture
def test_account(db_session):
    from tests.factories import AccountFactory
    AccountFactory._meta.sqlalchemy_session = db_session
    return AccountFactory()

@pytest.fixture
def sender_account(db_session):
    from tests.factories import AccountFactory
    AccountFactory._meta.sqlalchemy_session = db_session
    return AccountFactory()

@pytest.fixture
def receiver_account(db_session):
    from tests.factories import AccountFactory
    AccountFactory._meta.sqlalchemy_session = db_session
    return AccountFactory()
