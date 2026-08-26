import re

from pydantic import BaseModel, field_validator


TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class DoctorWorkingHoursCreate(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str

    @field_validator("day_of_week")
    @classmethod
    def validate_day_of_week(cls, value: int) -> int:
        if not 0 <= value <= 6:
            raise ValueError("day_of_week must be between 0 (Monday) and 6 (Sunday)")
        return value

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, value: str) -> str:
        if not TIME_PATTERN.match(value):
            raise ValueError("Time must be in HH:MM format (24-hour)")
        return value

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, value: str, info) -> str:
        start_time = info.data.get("start_time")
        if start_time and value <= start_time:
            raise ValueError("end_time must be after start_time")
        return value


class DoctorWorkingHoursOut(DoctorWorkingHoursCreate):
    working_hours_id: int
    doctor_id: int

    model_config = {"from_attributes": True}
