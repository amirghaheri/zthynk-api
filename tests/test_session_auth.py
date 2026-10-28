import hashlib
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.auth.dependencies import get_current_user
from app.db_models.organization import Organization
from app.db_models.session import UserSession
from app.db_models.user import User


def create_test_user(db_session):
    organization = Organization(name=f"Test Org {uuid4()}")
    db_session.add(organization)
    db_session.flush()

    user = User(
        email=f"{uuid4()}@example.com",
        name="Test User",
        organization_id=organization.id,
    )
    db_session.add(user)
    db_session.flush()

    return user


def create_test_session(db_session, user, token, expires_at, revoked_at=None):
    session = UserSession(
        user_id=user.id,
        session_token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        revoked_at=revoked_at,
    )
    db_session.add(session)
    db_session.flush()

    return session


def test_invalid_session_token_returns_401(client):
    response = client.get(
        "/services/",
        cookies={"zthynk_session": "invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired session"}


def test_expired_session_returns_401(client, db_session):
    user = create_test_user(db_session)
    token = "expired-test-token"

    create_test_session(
        db_session,
        user,
        token,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    response = client.get(
        "/services/",
        cookies={"zthynk_session": token},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired session"}


def test_revoked_session_returns_401(client, db_session):
    user = create_test_user(db_session)
    token = "revoked-test-token"
    now = datetime.now(timezone.utc)

    create_test_session(
        db_session,
        user,
        token,
        expires_at=now + timedelta(hours=1),
        revoked_at=now,
    )

    response = client.get(
        "/services/",
        cookies={"zthynk_session": token},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired session"}


def test_valid_session_authenticates_user(client, db_session):
    user = create_test_user(db_session)
    token = "valid-test-token"

    create_test_session(
        db_session,
        user,
        token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    response = client.get(
        "/services/",
        cookies={"zthynk_session": token},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_logout_revokes_session(client, db_session):
    user = create_test_user(db_session)
    token = "logout-test-token"

    session = create_test_session(
        db_session,
        user,
        token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    response = client.post(
        "/auth/logout",
        cookies={"zthynk_session": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/auth/success"

    db_session.refresh(session)
    assert session.revoked_at is not None


def test_logged_out_session_cannot_access_services(client, db_session):
    user = create_test_user(db_session)
    token = "logged-out-test-token"

    create_test_session(
        db_session,
        user,
        token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    logout_response = client.post(
        "/auth/logout",
        cookies={"zthynk_session": token},
        follow_redirects=False,
    )
    assert logout_response.status_code == 303

    services_response = client.get(
        "/services/",
        cookies={"zthynk_session": token},
    )

    assert services_response.status_code == 401
