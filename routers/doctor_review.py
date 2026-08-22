from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.doctor_review import DoctorReviewCreate, DoctorReviewOut, DoctorRatingSummary
from services.doctor_review_service import create_review, get_doctor_reviews, get_doctor_rating_summary
from core.security import get_current_user_id

router = APIRouter(prefix="/doctors", tags=["Doctor Reviews"])


@router.post("/reviews", response_model=DoctorReviewOut, status_code=201)
def add_review(
    data: DoctorReviewCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return create_review(db, current_user_id, data)


@router.get("/{doctor_id}/reviews", response_model=list[DoctorReviewOut])
def list_doctor_reviews(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    return get_doctor_reviews(db, doctor_id)


@router.get("/{doctor_id}/rating", response_model=DoctorRatingSummary)
def doctor_rating(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    return get_doctor_rating_summary(db, doctor_id)