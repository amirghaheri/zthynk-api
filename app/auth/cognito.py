from functools import lru_cache

import jwt
from jwt import PyJWKClient

from app.config.settings import settings

COGNITO_ISSUER = (
    f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/"
    f"{settings.cognito_user_pool_id}"
)

JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"


@lru_cache
def get_jwk_client() -> PyJWKClient:
    return PyJWKClient(JWKS_URL)


def verify_access_token(token: str) -> dict:
    jwk_client = get_jwk_client()

    signing_key = jwk_client.get_signing_key_from_jwt(token)

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=COGNITO_ISSUER,
        options={
            "verify_aud": False,
        },
    )

    if claims.get("token_use") != "access":
        raise ValueError("Token is not an access token")

    if claims.get("client_id") != settings.cognito_client_id:
        raise ValueError("Token was not issued for this application")

    return claims


def verify_id_token(token: str) -> dict:
    signing_key = get_jwk_client().get_signing_key_from_jwt(token)

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=COGNITO_ISSUER,
        audience=settings.cognito_client_id,
        options={
            "require": ["exp", "sub", "iss", "aud"],
        },
    )

    if claims.get("token_use") != "id":
        raise ValueError("Token is not an ID token")

    if not claims.get("email"):
        raise ValueError("ID token does not contain an email")

    if claims.get("email_verified") is not True:
        raise ValueError("Email address must be verified")

    return claims
