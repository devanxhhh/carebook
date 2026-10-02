from app.db.database import Base
from app.models.user import User
from app.models.centre import DiagnosticCentre
from app.models.test import DiagnosticTest, CentreTest
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.webhook import WebhookEvent

# This file imports all models to ensure they are registered with SQLAlchemy's Base.metadata
