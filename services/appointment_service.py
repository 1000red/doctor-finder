from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.appointment import Appointment
from models.doctor_availability import DoctorAvailability
from schemas.appointment import AppointmentCreate
from services.doctor_service import get_doctor_by_id

MAX_USERS_PER_SLOT = 3


def create_appointment(db: Session, user_id: int, data: AppointmentCreate) -> Appointment:
    if data.appointment_date < datetime.now(timezone.utc).date():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Appointments cannot be booked in the past")

    get_doctor_by_id(db, data.doctor_id)

    availability = (
        db.query(DoctorAvailability)
        .filter(
            DoctorAvailability.doctor_id == data.doctor_id,
            DoctorAvailability.day_of_week == data.appointment_date.day,
            DoctorAvailability.month == data.appointment_date.month,
            DoctorAvailability.year == data.appointment_date.year,
            DoctorAvailability.start_time == data.start_time,
            DoctorAvailability.end_time == data.end_time,
            DoctorAvailability.is_available == True,
        )
        .first()
    )

    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This time slot is not available")

    slot_key = f"appointment:{data.doctor_id}:{data.appointment_date.isoformat()}:{data.start_time}:{data.end_time}"
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:slot_key, 0))"), {"slot_key": slot_key})

    existing_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.user_id == user_id,
            Appointment.doctor_id == data.doctor_id,
            Appointment.appointment_date == data.appointment_date,
            Appointment.start_time == data.start_time,
            Appointment.end_time == data.end_time,
        )
        .first()
    )

    if existing_appointment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already booked this appointment")

    booked_count = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == data.doctor_id,
            Appointment.appointment_date == data.appointment_date,
            Appointment.start_time == data.start_time,
            Appointment.end_time == data.end_time,
        )
        .count()
    )

    if booked_count >= MAX_USERS_PER_SLOT:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This appointment is fully booked")

    appointment = Appointment(
        user_id=user_id,
        doctor_id=data.doctor_id,
        appointment_date=data.appointment_date,
        start_time=data.start_time,
        end_time=data.end_time,
        created_at=datetime.now(timezone.utc),
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment