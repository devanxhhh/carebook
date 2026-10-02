from datetime import datetime, timedelta, timezone
from unittest import mock
from concurrent.futures import ThreadPoolExecutor

from app.main import app
from app.db.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.centre import DiagnosticCentre
from app.models.test import DiagnosticTest, CentreTest
from tests.conftest import engine, _truncate_all

def test_webhook_success_updates_payment(client, normal_user_token, db_session, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    booking_resp = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    booking_id = booking_resp.json()["id"]

    from app.models.payment import Payment
    payment = db_session.query(Payment).filter(Payment.booking_id == booking_id).first()
    payment.provider_payment_id = "test_provider_id_1"
    db_session.commit()

    webhook_payload = {
        "event_id": "evt_1",
        "event_type": "payment.updated",
        "payment_id": str(payment.id),
        "provider_payment_id": "test_provider_id_1",
        "status": "SUCCESS"
    }
    resp = client.post("/api/v1/payments/webhook/", json=webhook_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "processed"

def test_webhook_idempotency_duplicate_event(client, normal_user_token, db_session, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    booking_resp = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    booking_id = booking_resp.json()["id"]

    from app.models.payment import Payment
    payment = db_session.query(Payment).filter(Payment.booking_id == booking_id).first()
    payment.provider_payment_id = "test_provider_id_2"
    db_session.commit()

    webhook_payload = {
        "event_id": "evt_2",
        "event_type": "payment.updated",
        "payment_id": str(payment.id),
        "provider_payment_id": "test_provider_id_2",
        "status": "SUCCESS"
    }
    
    resp1 = client.post("/api/v1/payments/webhook/", json=webhook_payload)
    assert resp1.status_code == 200

    resp2 = client.post("/api/v1/payments/webhook/", json=webhook_payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "already_processed"

def test_webhook_stale_failed_does_not_downgrade(client, normal_user_token, db_session, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    booking_resp = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    booking_id = booking_resp.json()["id"]

    from app.models.payment import Payment
    payment = db_session.query(Payment).filter(Payment.booking_id == booking_id).first()
    payment.provider_payment_id = "test_provider_id_3"
    db_session.commit()

    webhook_payload_success = {
        "event_id": "evt_3_success",
        "event_type": "payment.updated",
        "payment_id": str(payment.id),
        "provider_payment_id": "test_provider_id_3",
        "status": "SUCCESS"
    }
    client.post("/api/v1/payments/webhook/", json=webhook_payload_success)

    webhook_payload_failed = {
        "event_id": "evt_3_failed_late",
        "event_type": "payment.updated",
        "payment_id": str(payment.id),
        "provider_payment_id": "test_provider_id_3",
        "status": "FAILED"
    }
    client.post("/api/v1/payments/webhook/", json=webhook_payload_failed)

    booking_check = client.get(f"/api/v1/bookings/{booking_id}", headers={"Authorization": f"Bearer {normal_user_token}"})
    assert booking_check.json()["status"] == "CONFIRMED"

def test_webhook_invalid_payload_rejected(client):
    webhook_payload = {
        "event_id": "",
        "event_type": "payment.updated",
        "payment_id": "123",
        "provider_payment_id": "provider_123",
        "status": "INVALID_STATUS"
    }
    resp = client.post("/api/v1/payments/webhook/", json=webhook_payload)
    assert resp.status_code == 422

def test_webhook_nonexistent_payment_safely_ignored(client):
    webhook_payload = {
        "event_id": "evt_nonexistent",
        "event_type": "payment.updated",
        "payment_id": "9999",
        "provider_payment_id": "nonexistent_provider_id",
        "status": "SUCCESS"
    }
    resp = client.post("/api/v1/payments/webhook/", json=webhook_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored_payment_not_found"

def test_webhook_concurrent_requests(setup_db):
    """
    Tests that concurrent webhook requests with the same event_id are handled
    idempotently. Each thread gets its own independent DB session and HTTP client,
    simulating what happens in a real multi-process/multi-thread server environment.
    
    The database UNIQUE constraint on WebhookEvent.event_id is the final guarantee:
    only one INSERT can succeed; the rest receive an IntegrityError and return
    'already_processed'.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import sessionmaker
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Create independent sessions (each thread gets its own fresh session)
    thread_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # First, set up the fixture data using one session
    setup_session = thread_session_factory()
    try:
        centre = DiagnosticCentre(name="Concurrent Centre", location="Test City", is_active=True)
        setup_session.add(centre)
        test_obj = DiagnosticTest(name="Concurrent Test", code="CT_CONC", category="Test", is_active=True)
        setup_session.add(test_obj)
        setup_session.commit()
        ct = CentreTest(centre_id=centre.id, test_id=test_obj.id, price=300.0, is_available=True)
        setup_session.add(ct)

        normal_user_obj = User(
            name="Concurrent User",
            email="concurrent_user@test.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.USER,
        )
        setup_session.add(normal_user_obj)
        setup_session.commit()

        from app.models.booking import Booking, BookingStatus
        from app.models.payment import Payment, PaymentStatus
        from datetime import datetime, timedelta, timezone

        future_dt = datetime.now(timezone.utc) + timedelta(days=3)
        booking = Booking(
            user_id=normal_user_obj.id,
            centre_id=centre.id,
            test_id=test_obj.id,
            appointment_at=future_dt,
            amount=300.0,
            status=BookingStatus.PENDING,
        )
        setup_session.add(booking)
        setup_session.flush()
        booking_id = booking.id

        payment = Payment(
            booking_id=booking.id,
            amount=300.0,
            status=PaymentStatus.PENDING,
            provider_payment_id="concurrent_provider_id",
        )
        setup_session.add(payment)
        setup_session.commit()
        payment_id = payment.id
    finally:
        setup_session.close()

    webhook_payload = {
        "event_id": "evt_concurrent_unique_456",
        "event_type": "payment.updated",
        "payment_id": str(payment_id),
        "provider_payment_id": "concurrent_provider_id",
        "status": "SUCCESS",
    }

    def override_db():
        own_session = thread_session_factory()
        try:
            yield own_session
        except Exception:
            own_session.rollback()
            raise
        finally:
            own_session.close()

    def fire_webhook_independently(worker_id: int):
        with TestClient(app) as c:
            return c.post("/api/v1/payments/webhook/", json=webhook_payload)

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_db
    try:
        # Run 4 calls in parallel threads — the DB UNIQUE constraint ensures exactly 1 succeeds
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(fire_webhook_independently, i) for i in range(4)]
            results = [f.result() for f in futures]
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override

    statuses = [r.json()["status"] for r in results]
    assert statuses.count("processed") == 1, f"Expected exactly 1 processed, got: {statuses}"
    assert statuses.count("already_processed") == 3, f"Expected 3 already_processed, got: {statuses}"

    # Verify exactly one WebhookEvent row was created in the DB
    verify_session = thread_session_factory()
    try:
        from app.models.booking import Booking, BookingStatus
        from app.models.payment import Payment, PaymentStatus
        from app.models.webhook import WebhookEvent

        events = verify_session.query(WebhookEvent).filter(
            WebhookEvent.event_id == "evt_concurrent_unique_456"
        ).all()
        assert len(events) == 1, f"Expected 1 WebhookEvent, found {len(events)}"
        assert events[0].processed is True

        payment = verify_session.query(Payment).filter(Payment.id == payment_id).one()
        assert payment.status == PaymentStatus.SUCCESS

        verified_booking = verify_session.query(Booking).filter(Booking.id == booking_id).one()
        assert verified_booking.status == BookingStatus.CONFIRMED
    finally:
        verify_session.close()

    # Clean up test data so other tests start fresh
    with engine.connect() as conn:
        _truncate_all(conn)
