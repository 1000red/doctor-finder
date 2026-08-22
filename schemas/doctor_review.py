from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class DoctorReviewCreate(BaseModel):
    doctor_id: int
    rating: int = Field(..., ge=1, le=5)


class DoctorReviewOut(BaseModel):
    review_id: int
    user_id: int
    doctor_id: int
    rating: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DoctorRatingSummary(BaseModel):
    doctor_id: int
    average_rating: float