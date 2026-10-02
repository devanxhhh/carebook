def test_normal_user_cannot_create_centre(client, normal_user_token):
    response = client.post("/api/v1/centres", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "name": "User Centre",
        "location": "Some City"
    })
    assert response.status_code == 403

def test_normal_user_cannot_create_test(client, normal_user_token):
    response = client.post("/api/v1/tests", headers={"Authorization": f"Bearer {normal_user_token}"}, json={
        "name": "User Test",
        "code": "UT01"
    })
    assert response.status_code == 403

def test_admin_can_create_centre_and_test(client, admin_user_token):
    c_resp = client.post("/api/v1/centres", headers={"Authorization": f"Bearer {admin_user_token}"}, json={
        "name": "Admin Centre",
        "location": "Admin City"
    })
    assert c_resp.status_code == 201
    centre_id = c_resp.json()["id"]

    t_resp = client.post("/api/v1/tests", headers={"Authorization": f"Bearer {admin_user_token}"}, json={
        "name": "Admin Test",
        "code": "AT01"
    })
    assert t_resp.status_code == 201
    test_id = t_resp.json()["id"]
    
    # Negative price should be rejected by pydantic
    ct_resp = client.post(f"/api/v1/centres/{centre_id}/tests", headers={"Authorization": f"Bearer {admin_user_token}"}, json={
        "test_id": test_id,
        "price": -50.0
    })
    assert ct_resp.status_code == 422
    
    # Zero price should be rejected
    ct_resp_zero = client.post(f"/api/v1/centres/{centre_id}/tests", headers={"Authorization": f"Bearer {admin_user_token}"}, json={
        "test_id": test_id,
        "price": 0.0
    })
    assert ct_resp_zero.status_code == 422

    # Valid price
    ct_resp_valid = client.post(f"/api/v1/centres/{centre_id}/tests", headers={"Authorization": f"Bearer {admin_user_token}"}, json={
        "test_id": test_id,
        "price": 500.0
    })
    assert ct_resp_valid.status_code == 201
