from pydantic import BaseModel, EmailStr
from typing import Optional, Literal


# ── User ──────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: str
    gender: Literal["male", "female"]

class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    gender: Literal["male", "female"]
    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


# ── Auth responses ────────────────────────────────────────────────────────────

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


# ── OTP / Password reset ──────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp:   str


class ResetPasswordRequest(BaseModel):
    reset_token:  str
    new_password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    password: Optional[str] = None