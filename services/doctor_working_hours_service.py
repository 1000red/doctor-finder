from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.doctor_working_hours import DoctorWorkingHours
from services.doctor_service import get_doctor_by_id


def get_doctor_working_hours(db: Session, doctor_id: int) -> list[DoctorWorkingHours]:
    get_doctor_by_id(db, doctor_id)
    return (
        db.query(DoctorWorkingHours)
        .filter(DoctorWorkingHours.doctor_id == doctor_id)
        .order_by(DoctorWorkingHours.day_of_week)
        .all()
    )
