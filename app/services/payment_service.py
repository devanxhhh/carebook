from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import random
import uuid
from datetime import datetime, timezone

from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.webhook import WebhookEvent
from app.schemas.payment import PaymentRequest
from app.schemas.webhook import WebhookPayload
from app.core.config import settings

class PaymentService:
    @staticmethod
    def process_payment_simulation(db: Session, current_user: User, payment_req: PaymentRequest) -> Payment:
        query = db.query(Booking).filter(Booking.id == payment_req.booking_id)
        if current_user.role != UserRole.ADMIN:
            query = query.filter(Booking.user_id == current_user.id)
            
        booking = query.first()
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found or not accessible")
            
        if booking.status != BookingStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Booking is not in PENDING state"
            )

        payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")
            
        if payment.status == PaymentStatus.SUCCESS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already successful")

        # Simulate provider call
        is_success = random.randint(1, 100) <= settings.PAYMENT_SUCCESS_RATE
        
        provider_payment_id = f"sim_{uuid.uuid4().hex[:8]}"
        
        try:
            if is_success:
                payment.status = PaymentStatus.SUCCESS
                payment.provider_payment_id = provider_payment_id
                payment.provider = "SimulatedGateway"
                booking.status = BookingStatus.CONFIRMED
            else:
                payment.status = PaymentStatus.FAILED
                payment.provider_payment_id = provider_payment_id
                payment.provider = "SimulatedGateway"
                booking.status = BookingStatus.FAILED
                
            db.commit()
            db.refresh(payment)
            return payment
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Payment update failed")

    @staticmethod
    def process_webhook(db: Session, payload: WebhookPayload) -> str:
        # Create webhook event safely
        try:
            webhook_event = WebhookEvent(
                event_id=payload.event_id,
                event_type=payload.event_type,
                provider_payment_id=payload.provider_payment_id,
                payload=payload.model_dump()
            )
            db.add(webhook_event)
            db.flush() # Will raise IntegrityError if event_id already exists
        except IntegrityError:
            db.rollback()
            # Already processed, idempotent success
            return "already_processed"

        # Now we process the event
        # Assuming payload.payment_id corresponds to our Payment.id in this simulation
        # In a real scenario, provider_payment_id would be mapped
        payment = db.query(Payment).filter(
            Payment.provider_payment_id == payload.provider_payment_id
        ).first()

        if not payment:
            # Maybe the payment id was passed instead
            try:
                payment_id_int = int(payload.payment_id)
                payment = db.query(Payment).filter(Payment.id == payment_id_int).first()
            except ValueError:
                pass

        if not payment:
            db.rollback()
            # We acknowledge it so provider doesn't retry forever, but we can't process it
            return "ignored_payment_not_found"

        booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()

        # State transition logic
        if payload.status == "SUCCESS":
            # PENDING -> SUCCESS
            # FAILED -> SUCCESS (assuming retry is allowed by gateway)
            # SUCCESS -> SUCCESS (no op)
            payment.status = PaymentStatus.SUCCESS
            if booking and booking.status != BookingStatus.CANCELLED:
                booking.status = BookingStatus.CONFIRMED
        elif payload.status == "FAILED":
            # SUCCESS -> FAILED (Disallowed to downgrade)
            if payment.status != PaymentStatus.SUCCESS:
                payment.status = PaymentStatus.FAILED
                if booking and booking.status == BookingStatus.PENDING:
                    booking.status = BookingStatus.FAILED

        webhook_event.processed = True
        webhook_event.processed_at = datetime.now(timezone.utc)
        
        db.commit()
        return "processed"
