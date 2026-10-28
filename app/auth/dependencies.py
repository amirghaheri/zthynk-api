import hashlib
from datetime import datetime, timezone

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.db_models.session import UserSession
from app.db_models.user import User


def get_current_user(
    zthynk_session: str | None = Cookie(
        default=None,
        alias="zthynk_session",
    ),
    db: Session = Depends(get_db),
) -> User:
    # 1. Require a session cookie.
    if not zthynk_session:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # 2. Hash the cookie value. The database stores only its hash.
    token_hash = hashlib.sha256(zthynk_session.encode("utf-8")).hexdigest()

    # 3. Find a valid, non-revoked, unexpired session.
    now = datetime.now(timezone.utc)

    statement = select(UserSession).where(
        UserSession.session_token_hash == token_hash,
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > now,
    )

    session = db.scalar(statement)

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session",
        )

    # 4. Load the user associated with this session.
    user = db.get(User, session.user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User account not found",
        )

    return user
