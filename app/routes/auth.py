import base64
import hashlib
import secrets
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.schemas.user import UserResponse
from app.db_models.user import User

from app.auth.cognito import verify_access_token, verify_id_token
from app.services.registration_service import (
    RegistrationError,
    register_or_get_user,
)
from app.config.settings import settings
from app.database.dependencies import get_db
from app.services.auth_service import get_user_by_cognito_subject
from app.services.session_service import create_session, revoke_session

router = APIRouter(prefix="/auth", tags=["Authentication"])


CALLBACK_URL = settings.callback_url


@router.get("/callback", response_class=HTMLResponse)
async def auth_callback(
    code: str = Query(...),
    state: str = Query(...),
    saved_state: str | None = Cookie(
        default=None,
        alias="zthynk_oauth_state",
    ),
    code_verifier: str | None = Cookie(
        default=None,
        alias="zthynk_pkce_verifier",
    ),
    db: Session = Depends(get_db),
):
    # Validate the login attempt before exchanging the code.
    if not saved_state or not secrets.compare_digest(state, saved_state):
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state",
        )

    if not code_verifier:
        raise HTTPException(
            status_code=400,
            detail="Missing PKCE verifier",
        )

    credentials = base64.b64encode(
        f"{settings.cognito_client_id}:{settings.cognito_client_secret}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "authorization_code",
        "client_id": settings.cognito_client_id,
        "code": code,
        "redirect_uri": CALLBACK_URL,
        "code_verifier": code_verifier,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{settings.cognito_domain.rstrip('/')}/oauth2/token",
            headers=headers,
            data=data,
        )

    if response.status_code != 200:
        print(
            "Cognito token exchange failed:",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=400,
            detail="Cognito token exchange failed",
        )

    tokens = response.json()

    try:
        # Verify both tokens before trusting their claims.
        access_claims = verify_access_token(tokens["access_token"])
        id_claims = verify_id_token(tokens["id_token"])

    except (
        KeyError,
        ValueError,
        jwt.InvalidTokenError,
        jwt.PyJWKClientError,
    ) as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid Cognito authentication",
        ) from exc

    # Both tokens must identify the same Cognito user.
    if access_claims.get("sub") != id_claims.get("sub"):
        raise HTTPException(
            status_code=401,
            detail="Cognito token identity mismatch",
        )

    cognito_sub = id_claims["sub"]
    email = id_claims["email"]
    name = id_claims.get("name") or email.split("@")[0]

    try:
        user = register_or_get_user(
            db=db,
            cognito_sub=cognito_sub,
            email=email,
            name=name,
        )
    except RegistrationError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    # Create a ZTHYNK session after the account is resolved.
    raw_token, session = create_session(
        db=db,
        user_id=user.id,
    )

    result = RedirectResponse(
        url="/auth/success",
        status_code=303,
    )

    result.set_cookie(
        key="zthynk_session",
        value=raw_token,
        httponly=True,
        secure=settings.environment != "local",
        samesite="lax",
        max_age=8 * 60 * 60,
        path="/",
    )

    result.delete_cookie(
        "zthynk_oauth_state",
        path="/auth/callback",
    )
    result.delete_cookie(
        "zthynk_pkce_verifier",
        path="/auth/callback",
    )

    return result


@router.get("/success", response_class=HTMLResponse)
def auth_success():
    return HTMLResponse(
        "<h2>ZTHYNK authentication successful</h2>"
        "<p>Cognito login and access-token verification succeeded.</p>"
        "<p>You can close this tab.</p>"
    )


@router.get("/login")
def login():
    # Generate a unique value for this login attempt.
    state = secrets.token_urlsafe(32)

    # Generate the PKCE verifier and its SHA-256 challenge.
    code_verifier = secrets.token_urlsafe(64)

    challenge_bytes = hashlib.sha256(code_verifier.encode("ascii")).digest()

    code_challenge = (
        base64.urlsafe_b64encode(challenge_bytes).rstrip(b"=").decode("ascii")
    )

    # Save state and verifier in short-lived, HTTP-only cookies.
    # These cookies are for local development over HTTP.
    response = RedirectResponse(
        url=(
            f"{settings.cognito_domain.rstrip('/')}/login?"
            + urlencode(
                {
                    "client_id": settings.cognito_client_id,
                    "response_type": "code",
                    "scope": "openid email",
                    "redirect_uri": CALLBACK_URL,
                    "state": state,
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256",
                }
            )
        ),
        status_code=302,
    )

    response.set_cookie(
        key="zthynk_oauth_state",
        value=state,
        httponly=True,
        secure=settings.environment != "local",
        samesite="lax",
        max_age=300,
        path="/auth/callback",
    )

    response.set_cookie(
        key="zthynk_pkce_verifier",
        value=code_verifier,
        httponly=True,
        secure=settings.environment != "local",
        samesite="lax",
        max_age=300,
        path="/auth/callback",
    )
    return response


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/logout")
def logout(
    zthynk_session: str | None = Cookie(
        default=None,
        alias="zthynk_session",
    ),
    db: Session = Depends(get_db),
):
    if zthynk_session:
        revoke_session(db, zthynk_session)

    response = RedirectResponse(
        url="/auth/success",
        status_code=303,
    )
    response.delete_cookie(
        key="zthynk_session",
        path="/",
        httponly=True,
        secure=settings.environment != "local",
        samesite="lax",
    )

    return response
