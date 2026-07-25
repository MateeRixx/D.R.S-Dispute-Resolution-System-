import pytest
from httpx import AsyncClient


@pytest.fixture
async def user(client: AsyncClient) -> dict:
    resp = await client.post("/users/", json={"full_name": "Alice", "email": "alice@example.com"})
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def merchant(client: AsyncClient) -> dict:
    resp = await client.post("/merchants/", json={"business_name": "Acme Corp"})
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_create_dispute_success(client: AsyncClient, user: dict, merchant: dict):
    payload = {
        "transaction_id": "TXN-001",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "4999.00",
        "currency": "INR",
        "reason_code": "ITEM_DEFECTIVE",
        "user_narrative": "Received a damaged phone.",
    }
    resp = await client.post("/disputes/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "INITIATED"
    assert data["transaction_id"] == "TXN-001"
    assert data["user_id"] == user["id"]
    assert data["merchant_id"] == merchant["id"]
    assert data["reason_code"] == "ITEM_DEFECTIVE"
    assert data["amount"] == "4999.00"
    assert len(data["audit_trail"]) == 1
    assert data["audit_trail"][0]["action_taken"] == "DISPUTE_CREATED"


@pytest.mark.asyncio
async def test_create_dispute_invalid_user_id(client: AsyncClient, merchant: dict):
    payload = {
        "transaction_id": "TXN-002",
        "user_id": "00000000-0000-0000-0000-000000000000",
        "merchant_id": merchant["id"],
        "amount": "1000.00",
        "currency": "INR",
        "reason_code": "ITEM_NOT_RECEIVED",
    }
    resp = await client.post("/disputes/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_dispute_with_fk_joined_data(client: AsyncClient, user: dict, merchant: dict):
    create_resp = await client.post("/disputes/", json={
        "transaction_id": "TXN-003",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "2500.00",
        "currency": "INR",
        "reason_code": "INCORRECT_AMOUNT",
    })
    assert create_resp.status_code == 201
    dispute_id = create_resp.json()["id"]

    get_resp = await client.get(f"/disputes/{dispute_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == dispute_id
    assert data["user_id"] == user["id"]
    assert data["merchant_id"] == merchant["id"]
    assert "evidence" in data
    assert "audit_trail" in data


@pytest.mark.asyncio
async def test_get_dispute_not_found(client: AsyncClient):
    resp = await client.get("/disputes/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    resp = await client.post("/users/", json={"full_name": "Bob", "email": "bob@example.com"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "bob@example.com"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient):
    await client.post("/users/", json={"full_name": "Charlie", "email": "charlie@example.com"})
    resp = await client.post("/users/", json={"full_name": "Charlie2", "email": "charlie@example.com"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_merchant_success(client: AsyncClient):
    resp = await client.post("/merchants/", json={"business_name": "Beta Inc"})
    assert resp.status_code == 201
    assert resp.json()["business_name"] == "Beta Inc"
