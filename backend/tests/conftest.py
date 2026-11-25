import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  注册全部模型
from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

TEST_DB_NAME = os.getenv("TEST_DB_NAME", "CampusMarketTest")

_url = make_url(settings.database_url)
_server_url = _url.set(database=None)
_admin_engine = create_engine(_server_url, isolation_level="AUTOCOMMIT")
with _admin_engine.connect() as connection:
    connection.execute(
        text(
            f"CREATE DATABASE IF NOT EXISTS `{TEST_DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    )

TEST_URL = _url.set(database=TEST_DB_NAME)
engine = create_engine(TEST_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False
)


@pytest.fixture(autouse=True)
def reset_database(tmp_path, monkeypatch):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "uploads"))
    yield


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_user():
    def _make_user(
        student_id: str,
        password: str | None = None,
        role: int = 0,
        status: int = 1,
        phone: str | None = None,
        nickname: str | None = None,
    ) -> int:
        session = TestingSessionLocal()
        user = User(
            student_id=student_id,
            password=hash_password(password or student_id),
            role=role,
            status=status,
            phone=phone,
            nickname=nickname,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
        session.close()
        return user_id

    return _make_user


@pytest.fixture
def token(client):
    def _token(student_id: str, password: str | None = None) -> str:
        response = client.post(
            "/api/v1/auth/login",
            json={
                "student_id": student_id,
                "password": password or student_id,
            },
        )
        assert response.status_code == 200, response.text
        return response.json()["data"]["access_token"]

    return _token


@pytest.fixture
def auth(token):
    def _auth(student_id: str, password: str | None = None) -> dict:
        return {"Authorization": f"Bearer {token(student_id, password)}"}

    return _auth


@pytest.fixture
def student(make_user, auth):
    make_user("20260001")
    return auth("20260001")


@pytest.fixture
def other_student(make_user, auth):
    make_user("20260002")
    return auth("20260002")


@pytest.fixture
def admin(make_user, auth):
    make_user("admin", role=2)
    return auth("admin")
