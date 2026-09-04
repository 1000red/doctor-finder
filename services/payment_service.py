import stripe
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.config import settings

from models.doctor import Doctor
from models.user import User

stripe.api_key = settings.STRIPE_SECRET_KEY

STRIPE_API_VERSION = "2024-06-20"


def create_payment_intent(db: Session, current_user: User, doctor_id: int):
    doctor = db.query(Doctor).filter(
        Doctor.doctor_id == doctor_id,
        Doctor.is_active == True,
    ).first()

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    amount_cents = int(doctor.price * 100)

    customer_id = getattr(current_user, "stripe_customer_id", None)

    if not customer_id:
        customer = stripe.Customer.create(
            name=current_user.full_name,
            email=current_user.email,
            metadata={"user_id": str(current_user.user_id)},
        )
        customer_id = customer["id"]

    ephemeral_key = stripe.EphemeralKey.create(
        customer=customer_id,
        stripe_version=STRIPE_API_VERSION,
    )

    payment_intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        customer=customer_id,
        automatic_payment_methods={"enabled": True},
        metadata={
            "user_id": str(current_user.user_id),
            "doctor_id": str(doctor_id),
        },
    )

    return {
        "client_secret": payment_intent["client_secret"],
        "ephemeral_key": ephemeral_key["secret"],
        "customer_id": customer_id,
    }