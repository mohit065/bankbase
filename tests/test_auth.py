def test_login_success(client, admin_user):
    response = client.post("/auth/login", data={"username": admin_user.email, "password": "adminpass"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure_wrong_password(client, admin_user):
    response = client.post("/auth/login", data={"username": admin_user.email, "password": "wrong"})
    assert response.status_code == 401

def test_login_failure_nonexistent_user(client):
    response = client.post("/auth/login", data={"username": "fake@example.com", "password": "fake"})
    assert response.status_code == 401

def test_change_password_success(client, clerk_user):
    login = client.post("/auth/login", data={"username": clerk_user.email, "password": "clerkpass"})
    token = login.json()["access_token"]

    response = client.post(
        "/auth/change-password",
        json={"current_password": "clerkpass", "new_password": "newclerkpass"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Password updated successfully"

    login2 = client.post("/auth/login", data={"username": clerk_user.email, "password": "newclerkpass"})
    assert login2.status_code == 200
    assert "access_token" in login2.json()

def test_change_password_wrong_current(client, admin_user):
    login = client.post("/auth/login", data={"username": admin_user.email, "password": "adminpass"})
    token = login.json()["access_token"]

    response = client.post(
        "/auth/change-password",
        json={"current_password": "wrongpass", "new_password": "newadminpass"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect"
