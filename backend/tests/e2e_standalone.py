"""
Standalone E2E test for DRS.
Run with: python tests/e2e_standalone.py

Requires the backend server to be running on http://localhost:8000.
"""

import asyncio
import json
import sys
import time
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = "http://localhost:8000"


def req(method, path, body=None, headers=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    r = Request(url, data=data, method=method, headers=req_headers)
    try:
        with urlopen(r) as resp:
            return resp.status, json.loads(resp.read().decode())
    except HTTPError as e:
        return e.code, json.loads(e.read().decode()) if e.read() else {"error": str(e)}


def test_health():
    status, data = req("GET", "/health")
    assert status == 200, f"Health check failed: {data}"
    assert data["status"] == "healthy"
    print("  [PASS] Health check")


def test_login():
    status, data = req("POST", "/auth/login", {"email": "e2e@demo.com", "role": "customer"})
    assert status == 200, f"Login failed: {data}"
    assert "access_token" in data
    assert data["role"] == "customer"
    print(f"  [PASS] Login — got token for {data['full_name']}")
    return data


def test_create_user_and_merchant():
    uid = uuid.uuid4().hex[:8]
    status, user = req("POST", "/users/", {"full_name": f"E2E-{uid}", "email": f"e2e-{uid}@test.com"})
    assert status == 201, f"Create user failed: {user}"
    print(f"  [PASS] Create user {user['email']}")

    status, merchant = req("POST", "/merchants/", {"business_name": "E2E Store"})
    assert status == 201, f"Create merchant failed: {merchant}"
    print(f"  [PASS] Create merchant {merchant['business_name']}")

    return user, merchant


def test_create_dispute(user, merchant):
    status, dispute = req("POST", "/disputes/", {
        "transaction_id": f"E2E-{uuid.uuid4().hex[:8].upper()}",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "4999.00",
        "currency": "INR",
        "reason_code": "ITEM_DEFECTIVE",
        "user_narrative": "Received a cracked screen smartphone.",
    })
    assert status == 201, f"Create dispute failed: {dispute}"
    assert dispute["status"] == "INITIATED"
    print(f"  [PASS] Create dispute {dispute['transaction_id']} (status: {dispute['status']})")
    return dispute


def test_upload_evidence(dispute_id):
    import http.client
    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="dispute_id"\r\n\r\n'
        f"{dispute_id}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="uploaded_by"\r\n\r\n'
        f"USER\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
        f"{b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'.decode('latin-1')}\r\n"
        f"--{boundary}--\r\n"
    ).encode("latin-1")

    conn = http.client.HTTPConnection("localhost", 8000)
    conn.request("POST", "/evidence/upload", body, {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    })
    resp = conn.getresponse()
    data = json.loads(resp.read().decode())
    assert resp.status == 201, f"Upload evidence failed: {data}"
    assert data["file_type"] == "image/jpeg"
    print(f"  [PASS] Upload evidence (type: {data['file_type']})")

    status, dispute = req("GET", f"/disputes/{dispute_id}")
    assert status == 200
    assert len(dispute["evidence"]) >= 1
    print(f"  [PASS] Evidence linked to dispute ({len(dispute['evidence'])} item(s))")


def test_get_portal_dispute(dispute_id):
    status, dispute = req("GET", f"/portal/disputes/{dispute_id}")
    assert status == 200
    assert dispute["id"] == dispute_id
    print(f"  [PASS] Portal dispute detail ({dispute['status']})")


def test_list_portal_disputes(user, merchant):
    status, data = req("GET", f"/portal/disputes?user_id={user['id']}")
    assert status == 200
    assert len(data) >= 1
    print(f"  [PASS] Portal dispute list by user ({len(data)} dispute(s))")

    status, data = req("GET", f"/portal/disputes?merchant_id={merchant['id']}")
    assert status == 200
    assert len(data) >= 1
    print(f"  [PASS] Portal dispute list by merchant ({len(data)} dispute(s))")


def test_admin_reset():
    status, data = req("POST", "/admin/reset")
    assert status == 200
    assert data["message"] == "Demo data reset successfully"

    status, disputes = req("GET", "/portal/disputes")
    assert status == 200
    assert len(disputes) == 1
    d = disputes[0]
    assert d["transaction_id"] == "TXN-DEMO-001"
    assert d["verdict"] == "REFUND_USER"
    assert d["confidence_score"] == "0.88"
    assert len(d["audit_trail"]) == 5
    assert len(d["evidence"]) == 1
    print(f"  [PASS] Admin reset + seed data verified ({d['transaction_id']} -> {d['verdict']})")


def main():
    print("\nDRS E2E Test Suite")
    print(f"{'='*50}")
    print(f"Server: {BASE_URL}")
    print()

    test_health()

    test_login()

    user, merchant = test_create_user_and_merchant()

    dispute = test_create_dispute(user, merchant)

    test_upload_evidence(dispute["id"])

    test_get_portal_dispute(dispute["id"])

    test_list_portal_disputes(user, merchant)

    test_admin_reset()

    print(f"\n{'='*50}")
    print("All E2E tests passed!")
    print(f"{'='*50}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
