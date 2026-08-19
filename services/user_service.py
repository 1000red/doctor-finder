from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.config import settings
from core.security import hash_password, verify_password
from models.user import User
from schemas.user import UserUpdate
from utils.email import send_welcome_email


# ── User CRUD ─────────────────────────────────────────────────────────────────

def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email, User.is_deleted == False).first()


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# ── Sign Up & Account Management ──────────────────────────────────────────────

def create_user(db: Session, first_name: str, last_name: str, email: str, password: str, phone: str, gender: str) -> User:
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    db.refresh(user)
    send_welcome_email(user.email, user.first_name, user.last_name)
    return user


def delete_account(db: Session, user_id: int, password: str | None = None) -> None:
    user = get_user_by_id(db, user_id)

    if user.password:
        if not password or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect")

    timestamp = int(datetime.now(timezone.utc).timestamp())
    prefix = f"deleted_{timestamp}_"
    user.email = (prefix + user.email)[:100]

    if user.google_id:
        user.google_id = (prefix + user.google_id)[:255]

    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()