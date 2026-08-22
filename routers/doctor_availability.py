from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.doctor_availability import DoctorAvailabilityOut
from services.doctor_availability_service import get_doctor_availability

router = APIRouter(prefix="/doctors", tags=["Doctor Availability"])


@router.get("/{doctor_id}/availability", response_model=list[DoctorAvailabilityOut])
def get_doctor_availability_list(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    return get_doctor_availability(db, doctor_id)