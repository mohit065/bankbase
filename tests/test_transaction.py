from datetime import datetime, timedelta, UTC

def test_create_deposit_transaction(non_admin_client, sender_account):
    res = non_admin_client.post("/transactions", json={
        "type": "deposit",
        "amount": 1000.0,
        "recv_id": sender_account.id
    })
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "deposit"
    assert data["recv_id"] == sender_account.id

def test_create_withdrawal_transaction(non_admin_client, sender_account):
    res = non_admin_client.post("/transactions", json={
        "type": "withdrawal",
        "amount": 500.0,
        "sender_id": sender_account.id
    })
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "withdrawal"
    assert data["sender_id"] == sender_account.id

def test_create_transfer_transaction(non_admin_client, sender_account, receiver_account):
    res = non_admin_client.post("/transactions", json={
        "type": "transfer",
        "amount": 250.0,
        "sender_id": sender_account.id,
        "recv_id": receiver_account.id
    })
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "transfer"
    assert data["sender_id"] == sender_account.id
    assert data["recv_id"] == receiver_account.id

def test_transaction_requires_positive_amount(non_admin_client, sender_account):
    res = non_admin_client.post("/transactions", json={
        "type": "withdrawal",
        "amount": 0,
        "sender_id": sender_account.id
    })
    assert res.status_code == 400

def test_transaction_missing_fields(non_admin_client, sender_account):
    res = non_admin_client.post("/transactions", json={
        "type": "transfer",
        "amount": 100
    })
    assert res.status_code == 400
    assert res.json()["detail"] == "Transfer must have both sender_id and recv_id"

def test_admin_can_reverse_transaction(admin_client, sender_account, receiver_account):
    tx_res = admin_client.post("/transactions", json={
        "type": "transfer",
        "amount": 300.0,
        "sender_id": sender_account.id,
        "recv_id": receiver_account.id
    })
    tx_id = tx_res.json()["id"]

    res = admin_client.post(f"/transactions/{tx_id}/reverse")
    assert res.status_code == 200
    data = res.json()
    assert data["original"]["reversed"] is True
    assert data["reversal"]["type"] == "reversal"

def test_clerk_cannot_reverse_transaction(non_admin_client, sender_account, receiver_account):
    tx_res = non_admin_client.post("/transactions", json={
        "type": "transfer",
        "amount": 200.0,
        "sender_id": sender_account.id,
        "recv_id": receiver_account.id
    })
    tx_id = tx_res.json()["id"]

    res = non_admin_client.post(f"/transactions/{tx_id}/reverse")
    assert res.status_code == 403

def test_filter_transactions_by_account(non_admin_client, sender_account, receiver_account):
    non_admin_client.post("/transactions", json={
        "type": "transfer",
        "amount": 50.0,
        "sender_id": sender_account.id,
        "recv_id": receiver_account.id
    })

    res = non_admin_client.get(f"/transactions/by-account/{sender_account.id}")
    assert res.status_code == 200
    assert any(tx["sender_id"] == sender_account.id for tx in res.json())

def test_filter_transactions_by_date(non_admin_client, sender_account, receiver_account):
    non_admin_client.post("/transactions", json={
        "type": "transfer",
        "amount": 60.0,
        "sender_id": sender_account.id,
        "recv_id": receiver_account.id
    })

    start = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    end = (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")

    res = non_admin_client.get(f"/transactions/by-date?start={start}&end={end}")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
