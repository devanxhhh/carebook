from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    centre_id = Column(Integer, ForeignKey("diagnostic_centres.id"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("diagnostic_tests.id"), nullable=False)
    appointment_at = Column(DateTime(timezone=True), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    centre = relationship("DiagnosticCentre", back_populates="bookings")
    test = relationship("DiagnosticTest", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
