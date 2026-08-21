from pydantic import BaseModel
from typing import Optional


class DoctorOut(BaseModel):
    doctor_id: int
    name: str
    image: Optional[str] = None
    work_place: Optional[str] = None
    experience: Optional[int] = None
    treated: int
    price: float
    is_active: bool
    category_id: int

    model_config = {"from_attributes": True}