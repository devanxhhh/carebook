from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    centre_id: int
    test_id: int
    appointment_at: datetime

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    user_id: int
    amount: float
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaginatedBookingResponse(BaseModel):
    items: list[BookingResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
