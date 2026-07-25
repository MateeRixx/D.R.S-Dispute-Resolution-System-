import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_dispute_and_upload_evidence(client: AsyncClient, user: dict, merchant: dict):
    resp = await client.post("/disputes/", json={
        "transaction_id": "E2E-TXN-001",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "2500.00",
        "currency": "INR",
        "reason_code": "ITEM_DEFECTIVE",
        "user_narrative": "Received a damaged product.",
    })
    assert resp.status_code == 201
    dispute = resp.json()
    dispute_id = dispute["id"]
    assert dispute["status"] == "INITIATED"
    assert dispute["transaction_id"] == "E2E-TXN-001"
    assert dispute["user_id"] == user["id"]
    assert dispute["merchant_id"] == merchant["id"]
    assert len(dispute["audit_trail"]) == 1
    assert dispute["audit_trail"][0]["action_taken"] == "DISPUTE_CREATED"

    image_content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    resp = await client.post(
        "/evidence/upload",
        data={"dispute_id": dispute_id, "uploaded_by": "USER"},
        files={"file": ("screen.jpg", image_content, "image/jpeg")},
    )
    assert resp.status_code == 201
    evidence = resp.json()
    assert evidence["dispute_id"] == dispute_id
    assert evidence["file_type"] == "image/jpeg"
    assert evidence["uploaded_by"] == "USER"

    resp = await client.get(f"/disputes/{dispute_id}")
    assert resp.status_code == 200
    d = resp.json()
    assert len(d["evidence"]) >= 1
    assert any(e["id"] == evidence["id"] for e in d["evidence"])


@pytest.mark.asyncio
async def test_auth_login_flow(client: AsyncClient):
    resp = await client.post("/auth/login", json={"email": "e2e@test.com", "role": "customer"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["full_name"] is not None
    assert data["role"] == "customer"


@pytest.mark.asyncio
async def test_portal_dispute_list(client: AsyncClient, user: dict, merchant: dict):
    await client.post("/disputes/", json={
        "transaction_id": "PORTAL-TXN-001",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "1000.00",
        "currency": "INR",
        "reason_code": "INCORRECT_AMOUNT",
    })
    resp = await client.get(f"/portal/disputes?user_id={user['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(d["transaction_id"] == "PORTAL-TXN-001" for d in data)


@pytest.mark.asyncio
async def test_merchant_dashboard_flow(client: AsyncClient, user: dict, merchant: dict):
    await client.post("/disputes/", json={
        "transaction_id": "MERCHANT-TXN-001",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "750.00",
        "currency": "INR",
        "reason_code": "ITEM_NOT_RECEIVED",
    })
    resp = await client.get(f"/portal/disputes?merchant_id={merchant['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(d["transaction_id"] == "MERCHANT-TXN-001" for d in data)


@pytest.mark.asyncio
async def test_evidence_upload_invalid_type(client: AsyncClient, user: dict, merchant: dict):
    resp = await client.post("/disputes/", json={
        "transaction_id": "EVID-INVALID-TXN",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "500.00",
        "currency": "INR",
        "reason_code": "INCORRECT_AMOUNT",
    })
    dispute_id = resp.json()["id"]
    resp = await client.post(
        "/evidence/upload",
        data={"dispute_id": dispute_id, "uploaded_by": "USER"},
        files={"file": ("doc.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_admin_reset(client: AsyncClient):
    resp = await client.post("/admin/reset")
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Demo data reset successfully"

    resp = await client.get("/portal/disputes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["transaction_id"] == "TXN-DEMO-001"
    assert data[0]["verdict"] == "REFUND_USER"
