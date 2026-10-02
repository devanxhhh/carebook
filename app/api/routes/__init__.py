from fastapi import APIRouter
from app.api.routes import auth, centres, tests, bookings, payments

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(centres.router, prefix="/centres", tags=["Diagnostic Centres"])
api_router.include_router(tests.router, prefix="/tests", tags=["Diagnostic Tests"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
