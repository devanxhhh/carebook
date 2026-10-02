from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.schemas.webhook import WebhookPayload, WebhookResponse
from app.services.payment_service import PaymentService

router = APIRouter()

@router.post("/", response_model=PaymentResponse)
def simulate_payment(
    payment_req: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simulates a payment processing attempt
    """
    return PaymentService.process_payment_simulation(db, current_user, payment_req)

@router.post("/webhook/", response_model=WebhookResponse)
def payment_webhook(
    payload: WebhookPayload,
    db: Session = Depends(get_db)
):
    """
    Idempotent webhook endpoint to process payment updates
    """
    result_status = PaymentService.process_webhook(db, payload)
    return {"status": result_status}
