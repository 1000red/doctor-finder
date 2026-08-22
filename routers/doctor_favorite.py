from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.security import get_current_user_id
from db.database import get_db
from schemas.doctor_favorite import DoctorFavoriteCreate, DoctorFavoriteOut
from services.doctor_favorite_service import add_favorite, remove_favorite, get_user_favorites

router = APIRouter(prefix="/favorites", tags=["Doctor Favorites"])


@router.post("", response_model=DoctorFavoriteOut, status_code=status.HTTP_201_CREATED)
def add_doctor_to_favorites(
    data: DoctorFavoriteCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return add_favorite(db, user_id, data.doctor_id)


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_doctor_from_favorites(
    doctor_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    remove_favorite(db, user_id, doctor_id)


@router.get("", response_model=list[DoctorFavoriteOut])
def list_favorites(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return get_user_favorites(db, user_id)