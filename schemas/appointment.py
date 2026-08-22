from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: date
    start_time: str
    end_time: str


class AppointmentOut(BaseModel):
    appointment_id: int
    doctor_id: int
    doctor_name: str
    appointment_date: date
    start_time: str
    end_time: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None