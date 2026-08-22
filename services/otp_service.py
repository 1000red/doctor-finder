from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import random
import string

from core.security import create_reset_token
from utils.email import send_otp_email
from core.config import settings
from services.user_service import get_user_by_email

_otp_store: dict[str, dict] = {}


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


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

    sent = send_otp_email(email, otp, user.full_name)

    if not sent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP email")

    return {"message": f"OTP sent to {email}. Valid for {settings.OTP_EXPIRE_MINUTES} minutes."}


def verify_otp(email: str, otp: str) -> str:
    record = _otp_store.get(email)
    if not record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No OTP requested for this email")

    if datetime.now(timezone.utc) > record["expires_at"]:
        del _otp_store[email]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired. Please request a new one.")

    if record["otp"] != otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    reset_token = create_reset_token(record["user_id"])
    del _otp_store[email]
    return reset_token