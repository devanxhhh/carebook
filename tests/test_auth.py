def test_signup_success(client):
    response = client.post("/api/v1/auth/signup", json={
        "name": "New User",
        "email": "new@test.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "new@test.com"

def test_signup_duplicate_email(client, normal_user):
    response = client.post("/api/v1/auth/signup", json={
        "name": "Duplicate User",
        "email": "user@test.com",
        "password": "password123"
    })
    assert response.status_code == 409

def test_login_success(client, normal_user):
    response = client.post("/api/v1/auth/login", data={
        "username": "user@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password(client, normal_user):
    response = client.post("/api/v1/auth/login", data={
        "username": "user@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_protected_endpoint(client, normal_user_token):
    # Without token
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    
    # With token
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {normal_user_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"
