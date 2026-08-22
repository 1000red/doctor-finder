from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from models.user import User
from core.security import create_access_token, create_refresh_token
from core.config import settings
from services.user_service import get_user_by_email


def google_login(db: Session, token: str) -> dict:
    try:
        google_user = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )

    google_id = google_user.get("sub")
    email = google_user.get("email")
    email_verified = google_user.get("email_verified", False)
    full_name = google_user.get("name", "Google User")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google account information"
        )

    if not email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google email is not verified"
        )

    # 1. Search by Google ID
    user = db.query(User).filter(
        User.google_id == google_id,
        User.is_deleted == False
    ).first()

    # 2. If not found, search by email
    if not user:
        user = get_user_by_email(db, email)

    # 3. Existing account
    if user:
        if not user.google_id:
            user.google_id = google_id
            db.commit()
            db.refresh(user)

    # 4. New account
    else:
        user = User(
            full_name=full_name,
            email=email,
            password=None,
            phone=None,
            gender=None,
            google_id=google_id,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token({
        "sub": str(user.user_id),
        "type": "user"
    })

    refresh_token = create_refresh_token(user.user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }