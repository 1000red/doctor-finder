from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.doctor_working_hours import DoctorWorkingHoursCreate, DoctorWorkingHoursOut
from services.doctor_working_hours_service import (
    get_doctor_working_hours,
    replace_doctor_working_hours,
)

router = APIRouter(prefix="/doctors", tags=["Doctor Working Hours"])


@router.get("/{doctor_id}/working-hours", response_model=list[DoctorWorkingHoursOut])
def get_working_hours(doctor_id: int, db: Session = Depends(get_db)):
    return get_doctor_working_hours(db, doctor_id)


@router.put("/{doctor_id}/working-hours", response_model=list[DoctorWorkingHoursOut])
def update_working_hours(
    doctor_id: int,
    hours: list[DoctorWorkingHoursCreate],
    db: Session = Depends(get_db),
):
    return replace_doctor_working_hours(db, doctor_id, hours)
