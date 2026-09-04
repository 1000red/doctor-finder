from datetime import datetime, timezone
import stripe
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from core.config import settings

from models.doctor import Doctor
from models.appointment import Appointment
from models.doctor_availability import DoctorAvailability
from schemas.appointment import AppointmentCreate
from services.doctor_service import get_doctor_by_id

MAX_USERS_PER_SLOT = 3

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_appointment(db: Session, user_id: int, data: AppointmentCreate) -> Appointment:
    if data.appointment_date < datetime.now(timezone.utc).date():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Appointments cannot be booked in the past",
        )

    get_doctor_by_id(db, data.doctor_id)

    slot_key = (
        f"appointment:{data.doctor_id}:"
        f"{data.appointment_date.isoformat()}:"
        f"{data.start_time}:{data.end_time}"
    )

    db.execute(
        text(
            "SELECT pg_advisory_xact_lock("
            "hashtextextended(:slot_key, 0))"
        ),
        {"slot_key": slot_key},
    )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This time slot is not available",
        )

    existing_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.user_id == user_id,
            Appointment.doctor_id == data.doctor_id,
            Appointment.appointment_date == data.appointment_date,
        )
        .first()
    )

    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an appointment with this doctor on this day",
        )

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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This appointment is fully booked",
        )

    _verify_payment_intent(db, user_id, data)

    appointment = Appointment(
        user_id=user_id,
        doctor_id=data.doctor_id,
        appointment_date=data.appointment_date,
        start_time=data.start_time,
        end_time=data.end_time,
        payment_intent_id=data.payment_intent_id,
        created_at=datetime.now(timezone.utc),
    )

    db.add(appointment)

    if booked_count + 1 >= MAX_USERS_PER_SLOT:
        availability.is_available = False

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This payment has already been used for another appointment",
        )

    db.refresh(appointment)
    return appointment


def _verify_payment_intent(db: Session, user_id: int, data: AppointmentCreate) -> None:
    already_used = (
        db.query(Appointment)
        .filter(Appointment.payment_intent_id == data.payment_intent_id)
        .first()
    )
    if already_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This payment has already been used for another appointment",
        )

    try:
        intent = stripe.PaymentIntent.retrieve(data.payment_intent_id)
    except stripe.error.InvalidRequestError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment reference",
        )

    if intent.status != "succeeded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment has not been completed",
        )

    metadata = intent.metadata.to_dict() if intent.metadata else {}

    if metadata.get("user_id") != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This payment does not belong to you",
        )

    if metadata.get("doctor_id") != str(data.doctor_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This payment does not match the selected doctor",
        )


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

    try:
        stripe.Refund.create(
            payment_intent=appointment.payment_intent_id,
            idempotency_key=f"refund_{appointment.payment_intent_id}",
        )
    except stripe.error.InvalidRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Refund failed: {e.user_message or 'invalid payment reference'}",
        )
    except stripe.error.StripeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not process refund at this time. Please try again shortly.",
        )

    db.delete(appointment)

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