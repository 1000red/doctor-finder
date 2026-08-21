from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from core.security import hash_password, verify_password, decode_token
from utils.email import send_password_changed_email
from services.user_service import get_user_by_id


def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> None:
    user = get_user_by_id(db, user_id)
    if not verify_password(old_password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Old password is incorrect")

    user.password = hash_password(new_password)
    db.commit()
    send_password_changed_email(user.email, user.full_name)


def reset_password(db: Session, reset_token: str, new_password: str) -> None:
    payload = decode_token(reset_token)
    if payload.get("purpose") != "reset":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token purpose")

    user = get_user_by_id(db, int(payload["sub"]))
    user.password = hash_password(new_password)
    db.commit()