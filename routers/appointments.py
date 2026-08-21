from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.security import get_current_user_id
from db.database import get_db
from schemas.appointment import AppointmentCreate, AppointmentOut
from services.appointment_service import create_appointment


router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def book_appointment(
    data: AppointmentCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Book a doctor's exact date and time slot.

    A slot can contain at most three different user bookings.
    """
    return create_appointment(db=db, user_id=user_id, data=data)
