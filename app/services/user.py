from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.db_models.user import User
from app.repositories.user import (
    create_user as create_user_repository,
    get_user as get_user_repository,
    get_users as get_users_repository,
)


class UserService:

    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        user: User,
    ) -> User:
        return create_user_repository(
            self.db,
            user,
        )

    def get_user(
        self,
        user_id: UUID,
    ) -> User | None:
        return get_user_repository(
            self.db,
            user_id,
        )

    def get_users(
        self,
    ) -> list[User]:
        return get_users_repository(
            self.db,
        )


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    return UserService(db)
