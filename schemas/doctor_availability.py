from datetime import date as date_type
from pydantic import BaseModel


class DoctorAvailabilityOut(BaseModel):
    availability_id: int
    doctor_id: int
    date: date_type
    start_time: str
    end_time: str
    is_available: bool

    model_config = {"from_attributes": True}