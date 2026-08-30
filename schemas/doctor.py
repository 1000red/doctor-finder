from typing import Optional
from pydantic import BaseModel

from schemas.doctor_working_hours import DoctorWorkingHoursOut
from schemas.doctor_availability import DoctorAvailabilityOut


class DoctorOut(BaseModel):
    doctor_id: int
    name: str
    image: Optional[str] = None
    work_place: Optional[str] = None
    experience: Optional[int] = None
    treated: int
    price: float
    average_rating: float
    is_active: bool

    category_name: str
    working_hours: list[DoctorWorkingHoursOut] = []
    availability: list[DoctorAvailabilityOut] = []

    model_config = {"from_attributes": True}