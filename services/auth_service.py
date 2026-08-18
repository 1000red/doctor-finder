from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

from services.user_service import get_user_by_email


def login_user(
    db: Session,
    email: str,
    password: str,
) -> dict:

    user = get_user_by_email(
        db,
        email,
    )

    if (
        not user
        or not user.password
        or not verify_password(
            password,
            user.password,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token({
        "sub": str(user.user_id),
    })

    refresh_token = create_refresh_token(
        user.user_id
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


def refresh_access_token(
    refresh_token: str,
) -> str:

    payload = decode_token(
        refresh_token
    )

    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing subject",
        )

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in refresh token",
        )

    return create_access_token({
        "sub": str(user_id),
    })