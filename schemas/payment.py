from pydantic import BaseModel
from datetime import date


class PaymentIntentRequest(BaseModel):
    doctor_id: int
    appointment_date: date
    start_time: str
    end_time: str


class PaymentIntentResponse(BaseModel):
    client_secret: str
    ephemeral_key: str
    customer_id: str