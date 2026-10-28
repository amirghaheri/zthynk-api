from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models.user_identity import UserIdentity


def get_user_by_cognito_subject(
    db: Session,
    cognito_sub: str,
):
    statement = (
        select(UserIdentity)
        .where(UserIdentity.provider == "cognito")
        .where(UserIdentity.subject == cognito_sub)
    )

    identity = db.scalar(statement)

    if identity is None:
        return None

    return identity.user
