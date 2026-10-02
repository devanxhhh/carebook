from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    category = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    centre_tests = relationship("CentreTest", back_populates="test")
    bookings = relationship("Booking", back_populates="test")

class CentreTest(Base):
    __tablename__ = "centre_tests"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("diagnostic_centres.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("diagnostic_tests.id"), nullable=False)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    centre = relationship("DiagnosticCentre", back_populates="centre_tests")
    test = relationship("DiagnosticTest", back_populates="centre_tests")

    __table_args__ = (
        UniqueConstraint('centre_id', 'test_id', name='uq_centre_test'),
    )
