import re
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator

TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: date
    start_time: str
    end_time: str

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        if not TIME_PATTERN.match(v):
            raise ValueError("Time must be in HH:MM format (24-hour)")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: str, info) -> str:
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class AppointmentOut(BaseModel):
    appointment_id: int
    doctor_id: int
    appointment_date: date
    start_time: str
    end_time: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserAppointmentOut(BaseModel):
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

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not TIME_PATTERN.match(v):
            raise ValueError("Time must be in HH:MM format (24-hour)")
        return v