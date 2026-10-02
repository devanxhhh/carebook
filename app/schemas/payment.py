from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.payment import PaymentStatus

class PaymentRequest(BaseModel):
    booking_id: int

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: float
    status: PaymentStatus
    provider: str | None = None
    provider_payment_id: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
