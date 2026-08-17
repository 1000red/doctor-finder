from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import settings


bearer_scheme = HTTPBearer()


# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    plain: str,
    hashed: str,
) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8"),
    )


# ── Access Token ──────────────────────────────────────────────────────────────

def create_access_token(
    data: dict,
    expires_minutes: int | None = None,
) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=(
            expires_minutes
            or settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode["exp"] = expire
    to_encode["token_type"] = "access"

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ── Refresh Token ─────────────────────────────────────────────────────────────

def create_refresh_token(
    user_id: int,
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "token_type": "refresh",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ── Reset Token ───────────────────────────────────────────────────────────────
# NOTE: This is now fully independent from create_access_token.
# Previously it called create_access_token(), which unconditionally set
# token_type="access". That meant a password-reset token could be used
# as a normal Bearer access token anywhere in the API (privilege escalation).
# It now has its own token_type="reset", so get_current_user_id() rejects it.

def create_reset_token(
    user_id: int,
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "token_type": "reset",
        "purpose": "reset",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ── Decode Token ──────────────────────────────────────────────────────────────

def decode_token(token: str) -> dict:

    try:

        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

    except JWTError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from e


# ── Dependency: Get Current User ID ───────────────────────────────────────────

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
) -> int:

    payload = decode_token(
        credentials.credentials
    )

    # Make sure this is an access token
    # (this alone now also rejects reset tokens, since their
    # token_type is "reset", not "access")
    if payload.get("token_type") != "access":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )

    user_id = payload.get("sub")

    if user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )

    return int(user_id)