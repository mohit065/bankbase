
from tests.factories import EmployeeFactory

def test_add_employee(admin_client):
    res = admin_client.post("/employees", json={
        "name": "New Clerk",
        "email": "clerk@example.com",
        "phone": "1234567890",
        "password": "securepass",
        "role": "clerk"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "New Clerk"
    assert data["email"] == "clerk@example.com"
    assert data["role"] == "clerk"
    assert "id" in data

def test_add_employee_requires_admin(non_admin_client):
    res = non_admin_client.post("/employees", json={
        "name": "Unauthorized",
        "email": "unauth@example.com",
        "phone": "1112223333",
        "password": "pass"
    })
    assert res.status_code == 403

def test_add_employee_duplicate_email(admin_client, db_session):
    emp = EmployeeFactory(email="dupe@example.com")
    db_session.commit()

    res = admin_client.post("/employees", json={
        "name": "Another",
        "email": "dupe@example.com",
        "phone": "0001112222",
        "password": "pass"
    })
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already exists"


def test_update_employee(admin_client, db_session):
    emp = EmployeeFactory(name="Old Name")
    db_session.commit()

    res = admin_client.patch(
        f"/employees/{emp.id}",
        json={"name": "Updated Name"},
    )

    assert res.status_code == 200
    assert res.json()["name"] == "Updated Name"

def test_update_employee_requires_admin(non_admin_client, db_session):
    emp = EmployeeFactory(name="Old Name")
    db_session.commit()

    res = non_admin_client.patch(f"/employees/{emp.id}", json={"name": "Hack"})
    assert res.status_code == 403

def test_get_employee(admin_client, db_session):
    emp = EmployeeFactory()
    db_session.commit()

    res = admin_client.get(f"/employees/{emp.id}")
    assert res.status_code == 200
    assert res.json()["email"] == emp.email


def test_get_employee_requires_auth(client):
    res = client.get("/employees/1")
    assert res.status_code == 401


def test_list_employees(admin_client, db_session):
    EmployeeFactory.create_batch(3)
    db_session.commit()

    res = admin_client.get("/employees")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 3


def test_list_employees_requires_auth(client):
    res = client.get("/employees")
    assert res.status_code == 401


def test_delete_employee(admin_client, db_session):
    emp = EmployeeFactory()
    db_session.commit()

    res = admin_client.delete(f"/employees/{emp.id}")
    assert res.status_code == 204


def test_cannot_delete_self(admin_client, admin_user):
    res = admin_client.delete(f"/employees/{admin_user.id}")
    assert res.status_code == 400
    assert res.json()["detail"] == "You cannot delete your own account"


def test_delete_employee_requires_admin(non_admin_client, db_session):
    emp = EmployeeFactory()
    db_session.commit()

    res = non_admin_client.delete(f"/employees/{emp.id}")
    assert res.status_code == 403


def test_get_nonexistent_employee(admin_client):
    res = admin_client.get("/employees/9999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Employee not found"
