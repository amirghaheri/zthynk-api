from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db_models.organization import Organization
from app.db_models.user import User
from app.db_models.user_identity import UserIdentity


class RegistrationError(Exception):
    pass


def register_or_get_user(
    db: Session,
    cognito_sub: str,
    email: str,
    name: str,
) -> User:
    email = email.strip().lower()

    # 1. Existing Cognito identity: return its linked user.
    identity = db.scalar(
        select(UserIdentity).where(
            UserIdentity.provider == "cognito",
            UserIdentity.subject == cognito_sub,
        )
    )

    if identity is not None:
        return identity.user

    # 2. Do not automatically link an existing account by email.
    existing_user = db.scalar(select(User).where(User.email == email))

    if existing_user is not None:
        raise RegistrationError(
            "An account with this email already exists. " "Account linking is required."
        )

    # 3. Create a new organization, user, and identity together.
    organization = Organization(name=f"{name}'s Workspace ({uuid4().hex[:8]})")

    try:
        db.add(organization)
        db.flush()  # Generate organization.id before creating the user.

        user = User(
            email=email,
            name=name,
            organization_id=organization.id,
        )
        db.add(user)
        db.flush()

        identity = UserIdentity(
            user_id=user.id,
            provider="cognito",
            subject=cognito_sub,
        )
        db.add(identity)

        db.commit()
        db.refresh(user)

        return user

    except IntegrityError as exc:
        db.rollback()

        # Another request may have registered this identity concurrently.
        identity = db.scalar(
            select(UserIdentity).where(
                UserIdentity.provider == "cognito",
                UserIdentity.subject == cognito_sub,
            )
        )

        if identity is not None:
            return identity.user

        raise RegistrationError(
            "Registration conflicted with an existing account. "
            "Please try again or contact support."
        ) from exc

    except Exception:
        db.rollback()
        raise
