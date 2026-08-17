from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.database import get_db

from schemas.user import (
    UserCreate,
    UserLogin,
    UserOut,
    TokenOut,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
)

from schemas.auth import RefreshTokenRequest, SocialLoginRequest

from service import user_service as svc


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# ── Sign Up ──────────────────────────────────────────────────────────────────

@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    return svc.create_user(
        db=db,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=data.password,
        phone=data.phone,
        gender=data.gender,
    )


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenOut,
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    return svc.login_user(
        db,
        data.email,
        data.password,
    )


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout")
def logout():
    return {
        "message": "Logged out successfully"
    }


# ── Forgot Password ───────────────────────────────────────────────────────────

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    return svc.request_otp(
        db,
        data.email,
    )


# ── Verify OTP ────────────────────────────────────────────────────────────────

@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPRequest,
):
    reset_token = svc.verify_otp(
        data.email,
        data.otp,
    )

    return {
        "message": "OTP verified.",
        "reset_token": reset_token,
    }


# ── Reset Password ────────────────────────────────────────────────────────────

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    svc.reset_password(
        db,
        data.reset_token,
        data.new_password,
    )

    return {
        "message": "Password reset successfully. You can now log in."
    }


# ── Refresh Token ─────────────────────────────────────────────────────────────

@router.post("/refresh")
def refresh_token(
    data: RefreshTokenRequest,
):
    access_token = svc.refresh_access_token(
        data.refresh_token
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post(
    "/google",
    response_model=TokenOut,
)
def google_login(
    data: SocialLoginRequest,
    db: Session = Depends(get_db),
):
    return svc.google_login(
        db,
        data.token,
    )