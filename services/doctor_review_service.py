from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.doctor import Doctor
from models.doctor_review import DoctorReview
from schemas.doctor_review import DoctorReviewCreate
from services.doctor_service import get_doctor_by_id


def create_review(db: Session, user_id: int, data: DoctorReviewCreate) -> DoctorReview:
    get_doctor_by_id(db, data.doctor_id)

    existing = db.query(DoctorReview).filter(
        DoctorReview.user_id == user_id, DoctorReview.doctor_id == data.doctor_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already rated this doctor")

    review = DoctorReview(user_id=user_id, doctor_id=data.doctor_id, rating=data.rating)
    db.add(review)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already rated this doctor")

    db.refresh(review)

    _update_doctor_average_rating(db, data.doctor_id)

    return review


def get_doctor_reviews(db: Session, doctor_id: int) -> list[DoctorReview]:
    get_doctor_by_id(db, doctor_id)
    return db.query(DoctorReview).filter(DoctorReview.doctor_id == doctor_id).all()


def _update_doctor_average_rating(db: Session, doctor_id: int) -> None:
    average = (
        db.query(func.avg(DoctorReview.rating))
        .filter(DoctorReview.doctor_id == doctor_id)
        .scalar()
    )

    db.query(Doctor).filter(Doctor.doctor_id == doctor_id).update(
        {"average_rating": round(average, 2) if average is not None else 0.0}
    )
    db.commit()