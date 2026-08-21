from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.doctor_favorite import DoctorFavorite
from services.doctor import get_doctor_by_id


def add_favorite(db: Session, user_id: int, doctor_id: int) -> DoctorFavorite:
    get_doctor_by_id(db, doctor_id)

    existing = db.query(DoctorFavorite).filter(DoctorFavorite.user_id == user_id, DoctorFavorite.doctor_id == doctor_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Doctor already added to favorites")

    favorite = DoctorFavorite(user_id=user_id, doctor_id=doctor_id)
    db.add(favorite)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Doctor already added to favorites")

    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user_id: int, doctor_id: int) -> None:
    favorite = db.query(DoctorFavorite).filter(DoctorFavorite.user_id == user_id, DoctorFavorite.doctor_id == doctor_id).first()
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")

    db.delete(favorite)
    db.commit()


def get_user_favorites(db: Session, user_id: int) -> list[DoctorFavorite]:
    return db.query(DoctorFavorite).filter(DoctorFavorite.user_id == user_id).all()