from datetime import datetime, timedelta, timezone

def test_create_booking_success(client, normal_user_token, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 500.0
    assert data["status"] == "PENDING"

def test_create_booking_invalid_centre(client, normal_user_token, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": 999,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    assert response.status_code == 400
    assert "centre" in response.json()["detail"].lower()

def test_create_booking_invalid_test(client, normal_user_token, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": 999,
        "appointment_at": future_date
    })
    assert response.status_code == 400
    assert "test" in response.json()["detail"].lower()

def test_create_booking_unavailable_combination(client, admin_user_token, normal_user_token, setup_catalogue):
    # Admin creates a new centre and test but doesn't link them
    c_resp = client.post("/api/v1/centres", headers={"Authorization": f"Bearer {admin_user_token}"}, json={
        "name": "Another Centre", "location": "Another City"
    })
    centre_id = c_resp.json()["id"]
    
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": centre_id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    assert response.status_code == 400
    assert "not available at this centre" in response.json()["detail"].lower()

def test_create_booking_inactive_centre(client, admin_user_token, normal_user_token, setup_catalogue):
    # Admin soft deletes centre
    client.delete(f"/api/v1/centres/{setup_catalogue['centre'].id}", headers={"Authorization": f"Bearer {admin_user_token}"})
    
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    assert response.status_code == 400
    assert "invalid or inactive centre" in response.json()["detail"].lower()

def test_create_booking_past_date(client, normal_user_token, setup_catalogue):
    past_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    response = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": past_date
    })
    assert response.status_code == 400

def test_get_own_booking(client, normal_user_token, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_resp = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    # Will fail if the centre was deleted by test_create_booking_inactive_centre
    # But since db_session fixture isolates tests by transaction rollback, it's safe.
    booking_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/v1/bookings/{booking_id}", headers={"Authorization": f"Bearer {normal_user_token}"})
    assert get_resp.status_code == 200

def test_cannot_get_others_booking(client, normal_user_token, admin_user_token, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_resp = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {admin_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    booking_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/v1/bookings/{booking_id}", headers={"Authorization": f"Bearer {normal_user_token}"})
    assert get_resp.status_code == 404

def test_cancel_booking(client, normal_user_token, setup_catalogue):
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_resp = client.post("/api/v1/bookings", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "centre_id": setup_catalogue["centre"].id,
        "test_id": setup_catalogue["test"].id,
        "appointment_at": future_date
    })
    booking_id = create_resp.json()["id"]

    cancel_resp = client.post(f"/api/v1/bookings/{booking_id}/cancel", headers={"Authorization": f"Bearer {normal_user_token}"})
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"
