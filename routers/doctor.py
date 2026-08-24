from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from db.database import get_db
from models.doctor import Doctor
from schemas.doctor import DoctorOut
from services.doctor_service import get_doctor_by_id, get_doctors, get_doctors_by_category, search_doctors

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def _build_doctor_out(doctor: Doctor, base_url: str) -> DoctorOut:
    return DoctorOut(
        doctor_id=doctor.doctor_id,
        name=doctor.name,
        image=f"{base_url}/image/{doctor.image}" if doctor.image else None,
        work_place=doctor.work_place,
        experience=doctor.experience,
        treated=doctor.treated,
        price=doctor.price,
        average_rating=doctor.average_rating,
        is_active=doctor.is_active,
        category_id=doctor.category_id,
    )


@router.get("/", response_model=list[DoctorOut])
def get_all_doctors(request: Request, db: Session = Depends(get_db)):
    base_url = str(request.base_url).rstrip("/")
    return [_build_doctor_out(d, base_url) for d in get_doctors(db)]


@router.get("/search", response_model=list[DoctorOut])
def search_doctors(query: str, request: Request, db: Session = Depends(get_db)):
    base_url = str(request.base_url).rstrip("/")
    return [_build_doctor_out(d, base_url) for d in search_doctors(db, query)]


@router.get("/category/{category_id}", response_model=list[DoctorOut])
def get_doctors_in_category(category_id: int, request: Request, db: Session = Depends(get_db)):
    base_url = str(request.base_url).rstrip("/")
    return [_build_doctor_out(d, base_url) for d in get_doctors_by_category(db, category_id)]


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: int, request: Request, db: Session = Depends(get_db)):
    base_url = str(request.base_url).rstrip("/")
    return _build_doctor_out(get_doctor_by_id(db, doctor_id), base_url)