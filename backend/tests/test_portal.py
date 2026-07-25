import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_disputes_empty(client: AsyncClient):
    resp = await client.get("/portal/disputes")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_disputes_by_user(client: AsyncClient, user: dict, merchant: dict):
    resp = await client.post("/disputes/", json={
        "transaction_id": "TXN-PORTAL-001",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "1500.00",
        "currency": "INR",
        "reason_code": "ITEM_NOT_RECEIVED",
    })
    assert resp.status_code == 201

    resp = await client.get(f"/portal/disputes?user_id={user['id']}")
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["transaction_id"] == "TXN-PORTAL-001"


@pytest.mark.asyncio
async def test_get_portal_dispute(client: AsyncClient, user: dict, merchant: dict):
    create_resp = await client.post("/disputes/", json={
        "transaction_id": "TXN-PORTAL-002",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "2000.00",
        "currency": "INR",
        "reason_code": "ITEM_DEFECTIVE",
    })
    assert create_resp.status_code == 201
    dispute_id = create_resp.json()["id"]

    resp = await client.get(f"/portal/disputes/{dispute_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == dispute_id


@pytest.mark.asyncio
async def test_get_portal_dispute_not_found(client: AsyncClient):
    resp = await client.get("/portal/disputes/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Dispute not found"


@pytest.mark.asyncio
async def test_list_disputes_by_status(client: AsyncClient, user: dict, merchant: dict):
    await client.post("/disputes/", json={
        "transaction_id": "TXN-PORTAL-003",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "3000.00",
        "currency": "INR",
        "reason_code": "INCORRECT_AMOUNT",
    })

    resp = await client.get("/portal/disputes?status=INITIATED")
    data = resp.json()
    assert len(data) >= 1
    for d in data:
        assert d["status"] == "INITIATED"
