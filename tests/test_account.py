def test_create_account_success(admin_client):
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "PID": "PID12345",
        "is_active": True
    }
    res = admin_client.post("/accounts", json=payload)
    assert res.status_code == 200
    assert res.json()["email"] == payload["email"]

def test_create_account_duplicate_email(admin_client, test_account):
    payload = {
        "name": "Another User",
        "email": test_account.email,
        "PID": "NEWPID00001",
        "is_active": True
    }
    res = admin_client.post("/accounts", json=payload)
    assert res.status_code == 400
    assert "Email already exists" in res.text

def test_create_account_duplicate_PID(admin_client, test_account):
    payload = {
        "name": "Another User",
        "email": "newuser@example.com",
        "PID": test_account.PID,
        "is_active": True
    }
    res = admin_client.post("/accounts", json=payload)
    assert res.status_code == 400
    assert "PID already exists" in res.text

def test_update_account(non_admin_client, test_account):
    res = non_admin_client.put(f"/accounts/{test_account.id}", json={
        "name": "Updated Name"
    })
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Name"

def test_get_account_by_id(non_admin_client, test_account):
    res = non_admin_client.get(f"/accounts/{test_account.id}")
    assert res.status_code == 200
    assert res.json()["id"] == test_account.id

def test_get_account_by_id_not_found(non_admin_client):
    res = non_admin_client.get("/accounts/99999")
    assert res.status_code == 404

def test_get_all_accounts(non_admin_client, test_account):
    res = non_admin_client.get("/accounts")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_toggle_account_active(admin_client, test_account):
    initial = test_account.is_active
    res = admin_client.patch(f"/accounts/{test_account.id}/toggle-active")
    assert res.status_code == 200
    assert res.json()["is_active"] != initial

def test_delete_account(admin_client, test_account):
    res = admin_client.delete(f"/accounts/{test_account.id}")
    assert res.status_code == 204

def test_delete_account_not_found(admin_client):
    res = admin_client.delete("/accounts/99999")
    assert res.status_code == 404
