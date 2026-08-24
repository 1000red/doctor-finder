from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.doctor import Doctor
from models.appointment import Appointment
from models.doctor_availability import DoctorAvailability
from schemas.appointment import AppointmentCreate
from services.doctor_service import get_doctor_by_id

MAX_USERS_PER_SLOT = 3


def create_appointment(db: Session, user_id: int, data: AppointmentCreate) -> Appointment:
    if data.appointment_date < datetime.now(timezone.utc).date():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Appointments cannot be booked in the past")

    get_doctor_by_id(db, data.doctor_id)

    slot_key = f"appointment:{data.doctor_id}:{data.appointment_date.isoformat()}:{data.start_time}:{data.end_time}"
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:slot_key, 0))"), {"slot_key": slot_key})

    availability = (
        db.query(DoctorAvailability)
        .filter(
            DoctorAvailability.doctor_id == data.doctor_id,
            DoctorAvailability.date == data.appointment_date,
            DoctorAvailability.start_time == data.start_time,
            DoctorAvailability.end_time == data.end_time,
            DoctorAvailability.is_available == True,
        )
        .first()
    )

    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This time slot is not available")

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

    # If this booking fills the slot, mark it unavailable so it stops
    # showing up in "available slots" listings elsewhere in the app.
    if booked_count + 1 >= MAX_USERS_PER_SLOT:
        availability.is_available = False

    db.commit()
    db.refresh(appointment)
    return appointment


def get_user_appointments(db: Session, user_id: int) -> list[dict]:
    results = (
        db.query(Appointment, Doctor.name.label("doctor_name"))
        .join(Doctor, Appointment.doctor_id == Doctor.doctor_id)
        .filter(Appointment.user_id == user_id)
        .order_by(Appointment.appointment_date, Appointment.start_time)
        .all()
    )

    return [
        {
            "appointment_id": appointment.appointment_id,
            "doctor_id": appointment.doctor_id,
            "doctor_name": doctor_name,
            "appointment_date": appointment.appointment_date,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time,
            "created_at": appointment.created_at,
        }
        for appointment, doctor_name in results
    ]


def cancel_appointment(db: Session, user_id: int, appointment_id: int) -> None:
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.appointment_id == appointment_id,
            Appointment.user_id == user_id,
        )
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    db.delete(appointment)

    # Re-open the slot since a spot just freed up.
    availability = (
        db.query(DoctorAvailability)
        .filter(
            DoctorAvailability.doctor_id == appointment.doctor_id,
            DoctorAvailability.date == appointment.appointment_date,
            DoctorAvailability.start_time == appointment.start_time,
            DoctorAvailability.end_time == appointment.end_time,
        )
        .first()
    )
    if availability and not availability.is_available:
        availability.is_available = True

    db.commit()