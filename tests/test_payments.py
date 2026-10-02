from datetime import datetime, timedelta, timezone
from unittest import mock
import pytest

@pytest.fixture
def test_booking(client, normal_user_token, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    return response.json()

def test_payment_simulation_success(client, normal_user_token, test_booking):
    with mock.patch("app.services.payment_service.random.randint", return_value=1):
        response = client.post("/api/v1/payments/", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
            "booking_id": test_booking["id"]
        })
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

        booking_resp = client.get(f"/api/v1/bookings/{test_booking['id']}", headers={"Authorization": f"Bearer {normal_user_token}"})
        assert booking_resp.json()["status"] == "CONFIRMED"

def test_payment_simulation_failure(client, normal_user_token, test_booking):
    with mock.patch("app.services.payment_service.random.randint", return_value=100):
        response = client.post("/api/v1/payments/", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
            "booking_id": test_booking["id"]
        })
        assert response.status_code == 200
        assert response.json()["status"] == "FAILED"

        booking_resp = client.get(f"/api/v1/bookings/{test_booking['id']}", headers={"Authorization": f"Bearer {normal_user_token}"})
        assert booking_resp.json()["status"] == "FAILED"

def test_duplicate_payment_fails(client, normal_user_token, test_booking):
    with mock.patch("app.services.payment_service.random.randint", return_value=1):
        client.post("/api/v1/payments/", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
            "booking_id": test_booking["id"]
        })
        
        response = client.post("/api/v1/payments/", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
            "booking_id": test_booking["id"]
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Booking is not in PENDING state"
