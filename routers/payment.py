from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.payment import PaymentIntentRequest, PaymentIntentResponse
from services.payment_service import create_payment_intent
from core.security import get_current_user_id
from models.user import User

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/intent", response_model=PaymentIntentResponse)
def create_intent(
    payload: PaymentIntentRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    current_user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not current_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return create_payment_intent(
        db=db,
        current_user=current_user,
        doctor_id=payload.doctor_id,
    )