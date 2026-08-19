from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from core.security import get_current_user_id
from schemas.user import UserOut, UserUpdate, ChangePasswordRequest, DeleteAccountRequest
from services import get_user_by_id, update_user, change_password, delete_account

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return get_user_by_id(db, user_id)


@router.put("/me", response_model=UserOut)
def update_me(data: UserUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return update_user(db, user_id, data)


@router.put("/me/password")
def change_password_route(data: ChangePasswordRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    change_password(db, user_id, data.old_password, data.new_password)
    return {"message": "Password changed successfully"}


@router.delete("/me")
def delete_account_route(data: DeleteAccountRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    delete_account(db, user_id, data.password)
    return {"message": "Account deleted successfully"}