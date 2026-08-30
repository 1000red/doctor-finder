from typing import Optional
from pydantic import BaseModel
from schemas.doctor import DoctorOut


class CategoryOut(BaseModel):
    category_id: int
    name: str
    image: Optional[str] = None
    doctors: list[DoctorOut] = []

    model_config = {"from_attributes": True}