from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.doctor import Doctor
from services.category_service import get_category_by_id


def get_doctor_by_id(db: Session, doctor_id: int) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id, Doctor.is_active == True).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor


def get_doctors(db: Session) -> list[Doctor]:
    return db.query(Doctor).filter(Doctor.is_active == True).all()


def get_doctors_by_category(db: Session, category_id: int) -> list[Doctor]:
    get_category_by_id(db, category_id)
    return db.query(Doctor).filter(Doctor.category_id == category_id, Doctor.is_active == True).all()


# def search_doctors(db: Session, query: str) -> list[Doctor]:
#     q = query.strip()
#     if not q:
#         return []

#     return db.query(Doctor).filter(Doctor.name.ilike(f"{q}%"), Doctor.is_active == True).limit(20).all()


def search_doctors(db: Session, query: str) -> list[Doctor]:
    q = query.strip()
    if not q:
        return []

    return (
        db.query(Doctor)
        .filter(
            Doctor.name.ilike(f"%{q}%"),
            Doctor.is_active == True
        )
        .limit(20)
        .all()
    )