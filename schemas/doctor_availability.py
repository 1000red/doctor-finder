from pydantic import BaseModel
from typing import Optional

class DoctorAvailabilityOut(BaseModel):
    availability_id: int
    doctor_id: int
    day_of_week: int
    month: int
    year: int
    start_time: str
    end_time: str
    is_available: bool

    model_config = {"from_attributes": True}
