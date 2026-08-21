from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DoctorReviewCreate(BaseModel):
    doctor_id: int
    rating: int


class DoctorReviewOut(BaseModel):
    review_id: int
    user_id: int
    doctor_id: int
    rating: int
    created_at: datetime

    model_config = {"from_attributes": True}