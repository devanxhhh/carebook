from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Tuple, List
from datetime import datetime, timezone
import math

from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.models.centre import DiagnosticCentre
from app.models.test import DiagnosticTest, CentreTest
from app.models.payment import Payment, PaymentStatus
from app.schemas.booking import BookingCreate

class BookingService:
    @staticmethod
    def create_booking(db: Session, current_user: User, booking_in: BookingCreate) -> Booking:
        if booking_in.appointment_at.tzinfo is None:
            appointment_at = booking_in.appointment_at.replace(tzinfo=timezone.utc)
        else:
            appointment_at = booking_in.appointment_at

        if appointment_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment must be in the future"
            )

        centre = db.query(DiagnosticCentre).filter(
            DiagnosticCentre.id == booking_in.centre_id,
            DiagnosticCentre.is_active == True
        ).first()
        if not centre:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or inactive centre")

        test = db.query(DiagnosticTest).filter(
            DiagnosticTest.id == booking_in.test_id,
            DiagnosticTest.is_active == True
        ).first()
        if not test:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or inactive test")

        centre_test = db.query(CentreTest).filter(
            CentreTest.centre_id == booking_in.centre_id,
            CentreTest.test_id == booking_in.test_id,
            CentreTest.is_available == True
        ).first()

        if not centre_test:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test is not available at this centre"
            )

        # Start atomic transaction implicitly with db.add
        try:
            booking = Booking(
                user_id=current_user.id,
                centre_id=booking_in.centre_id,
                test_id=booking_in.test_id,
                appointment_at=appointment_at,
                amount=centre_test.price,
                status=BookingStatus.PENDING
            )
            db.add(booking)
            db.flush() # flush to get booking.id

            # Create an associated payment record
            payment = Payment(
                booking_id=booking.id,
                amount=booking.amount,
                status=PaymentStatus.PENDING
            )
            db.add(payment)
            
            db.commit()
            db.refresh(booking)
            return booking
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create booking: {str(e)}"
            )

    @staticmethod
    def get_bookings(
        db: Session, 
        current_user: User, 
        page: int = 1, 
        page_size: int = 10,
        booking_status: BookingStatus | None = None
    ) -> Tuple[List[Booking], int]:
        
        query = db.query(Booking)
        if current_user.role != UserRole.ADMIN:
            query = query.filter(Booking.user_id == current_user.id)
            
        if booking_status:
            query = query.filter(Booking.status == booking_status)
            
        total = query.count()
        items = query.order_by(Booking.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def get_booking(db: Session, current_user: User, booking_id: int) -> Booking:
        query = db.query(Booking).filter(Booking.id == booking_id)
        if current_user.role != UserRole.ADMIN:
            query = query.filter(Booking.user_id == current_user.id)
            
        booking = query.first()
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found or not accessible")
        return booking

    @staticmethod
    def cancel_booking(db: Session, current_user: User, booking_id: int) -> Booking:
        booking = BookingService.get_booking(db, current_user, booking_id)
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.FAILED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Cannot cancel booking with status {booking.status.value}"
            )
            
        booking.status = BookingStatus.CANCELLED
        db.commit()
        db.refresh(booking)
        return booking
