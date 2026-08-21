from datetime import datetime
from pydantic import BaseModel


class DoctorFavoriteCreate(BaseModel):
    doctor_id: int


class DoctorFavoriteOut(BaseModel):
    favorite_id: int
    user_id: int
    doctor_id: int
    created_at: datetime

    model_config = {"from_attributes": True}