import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db_models.session import UserSession

SESSION_DURATION = timedelta(hours=8)


def create_session(
    db: Session,
    user_id: UUID,
) -> tuple[str, UserSession]:
    # Generate a random secret for the browser.
    raw_token = secrets.token_urlsafe(32)

    # Store only the SHA-256 hash in PostgreSQL.
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    # Use timezone-aware UTC timestamps.
    now = datetime.now(timezone.utc)

    session = UserSession(
        user_id=user_id,
        session_token_hash=token_hash,
        created_at=now,
        expires_at=now + SESSION_DURATION,
    )

    try:
        db.add(session)
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise

    # Return the raw token for the cookie and the DB record.
    return raw_token, session


def revoke_session(
    db: Session,
    raw_token: str,
) -> bool:
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    statement = select(UserSession).where(
        UserSession.session_token_hash == token_hash,
        UserSession.revoked_at.is_(None),
    )

    session = db.scalar(statement)

    if session is None:
        return False

    session.revoked_at = datetime.now(timezone.utc)

    try:
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
