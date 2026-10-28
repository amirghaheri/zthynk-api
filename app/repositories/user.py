from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models.user import User


def create_user(
    db: Session,
    user: User,
) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(
    db: Session,
    user_id: UUID,
) -> User | None:
    return db.get(User, user_id)


def get_users(
    db: Session,
) -> list[User]:
    stmt = select(User)
    result = db.execute(stmt)

    return result.scalars().all()
