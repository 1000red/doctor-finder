from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.doctor_availability import DoctorAvailability
from services.doctor import get_doctor_by_id


def get_availability_by_id(db: Session, availability_id: int) -> DoctorAvailability:
    availability = db.query(
        DoctorAvailability).filter(DoctorAvailability.availability_id == availability_id).first()
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found")
    return availability


def get_doctor_availability(db: Session, doctor_id: int) -> list[DoctorAvailability]:
    get_doctor_by_id(db, doctor_id)
    return db.query(DoctorAvailability).filter(DoctorAvailability.doctor_id == doctor_id, DoctorAvailability.is_available == True).all()



