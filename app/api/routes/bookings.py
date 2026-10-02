from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.booking import BookingStatus
from app.schemas.booking import (
    BookingResponse,
    PaginatedBookingResponse,
    BookingCreate
)
from app.services.booking_service import BookingService

router = APIRouter()

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return BookingService.create_booking(db, current_user, booking_in)

@router.get("", response_model=PaginatedBookingResponse)
def list_bookings(
    booking_status: Optional[BookingStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items, total = BookingService.get_bookings(db, current_user, page, page_size, booking_status)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return BookingService.get_booking(db, current_user, booking_id)

@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return BookingService.cancel_booking(db, current_user, booking_id)
