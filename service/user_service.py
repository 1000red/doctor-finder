from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import random
import string
from google.oauth2 import id_token

from google.auth.transport import requests as google_requests
from models.user import User
from schemas.user import UserUpdate
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_reset_token,
    decode_token,
    create_refresh_token
)
from utils.email import (
    send_otp_email,
    send_welcome_email,
    send_password_changed_email,
)
from core.config import settings


_otp_store: dict[str, dict] = {}


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


# ── User CRUD ─────────────────────────────────────────────────────────────────

def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(
        User.user_id == user_id,
        User.is_deleted == False
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# ── Auth ──────────────────────────────────────────────────────────────────────

def login_user(
    db: Session,
    email: str,
    password: str,
) -> dict:

    user = get_user_by_email(
        db,
        email,
    )

    # NOTE: also guard against user.password being None — accounts created
    # via Google/Facebook login have no password set, and calling
    # verify_password(password, None) would raise an unhandled AttributeError
    # (500) instead of a clean 401.
    if not user or not user.password or not verify_password(
        password,
        user.password,
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

def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> None:
    user = get_user_by_id(db, user_id)
    if not verify_password(old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect"
        )
    user.password = hash_password(new_password)
    db.commit()
    send_password_changed_email(user.email, f"{user.first_name} {user.last_name}")

# ── OTP / Password ─────────────────────────────────────────────────────

def request_otp(db: Session, email: str) -> dict:
    user = get_user_by_email(db, email)
    if not user:
        return {"message": "If this email is registered, you will receive an OTP."}

    otp = _generate_otp()
    _otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        "user_id": user.user_id,
    }

    sent = send_otp_email(email, otp, user.first_name, user.last_name)
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email",
        )

    result: dict = {
        "message": f"OTP sent to {email}. Valid for {settings.OTP_EXPIRE_MINUTES} minutes."
    }
    if not settings.SENDGRID_API_KEY:
        result["debug_otp"] = otp
    return result


def verify_otp(email: str, otp: str) -> str:
    record = _otp_store.get(email)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP requested for this email"
        )
    if datetime.now(timezone.utc) > record["expires_at"]:
        del _otp_store[email]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )
    if record["otp"] != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    reset_token = create_reset_token(record["user_id"])
    del _otp_store[email]
    return reset_token


def reset_password(db: Session, reset_token: str, new_password: str) -> None:
    payload = decode_token(reset_token)
    if payload.get("purpose") != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token purpose"
        )
    user = get_user_by_id(db, int(payload["sub"]))
    user.password = hash_password(new_password)
    db.commit()


# ── sing up ─────────────────────────────────────────────────────


from sqlalchemy.exc import IntegrityError

def create_user(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: str,
    gender: str,
) -> User:

    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=hash_password(password),
        phone=phone,
        gender=gender,
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    db.refresh(user)

    send_welcome_email(
        user.email,
        user.first_name, 
        user.last_name,
    )

    return user


def google_login(db: Session, token: str) -> dict:
    try:
        google_user = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    google_id = google_user.get("sub")
    email = google_user.get("email")
    email_verified = google_user.get("email_verified", False)

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google account information",
        )

    if not email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google email is not verified",
        )

    first_name = google_user.get("given_name", "")
    last_name = google_user.get("family_name", "")

    # 1. Search by Google ID
    # NOTE: filter is_deleted here too — this is a direct query, not routed
    # through get_user_by_email, so it must repeat the same filter or a
    # deleted account could still be matched and reused.
    user = (
        db.query(User)
        .filter(
            User.google_id == google_id,
            User.is_deleted == False,
        )
        .first()
    )

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
            first_name=first_name or "Google",
            last_name=last_name or "User",
            email=email,
            password=None,
            phone=None,
            gender=None,
            google_id=google_id,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        {
            "sub": str(user.user_id),
            "type": "user",
        }
    )

    refresh_token = create_refresh_token(user.user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


def delete_account(db: Session, user_id: int, password: str | None = None) -> None:
    user = get_user_by_id(db, user_id)

    if user.password:
        if not password or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is incorrect"
            )
    # لو الحساب social-only (مفيش password)، بنعتمد بس على إنه معمول له login
    # (يعني الـ JWT بتاعه صالح) كتأكيد كافي حالياً.

    timestamp = int(datetime.now(timezone.utc).timestamp())
    prefix = f"deleted_{timestamp}_"
    user.email = (prefix + user.email)[:100]
    if user.google_id:
        user.google_id = (prefix + user.google_id)[:255]
   

    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()