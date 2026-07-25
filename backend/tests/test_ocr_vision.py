import io
import uuid
from pathlib import Path

import pytest
from httpx import AsyncClient
from PIL import Image

from app.models.dispute_models import EvidenceSource


def _make_test_image(format="JPEG", size=(100, 100)):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color="red")
    img.save(buf, format=format)
    buf.seek(0)
    return buf


@pytest.fixture
async def dispute(client: AsyncClient, user: dict, merchant: dict) -> dict:
    resp = await client.post("/disputes/", json={
        "transaction_id": "TXN-EV-001",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "1500.00",
        "currency": "INR",
        "reason_code": "ITEM_DEFECTIVE",
    })
    return resp.json()


@pytest.mark.asyncio
async def test_upload_evidence_success(client: AsyncClient, dispute: dict):
    img = _make_test_image()
    resp = await client.post(
        "/evidence/upload",
        data={"dispute_id": dispute["id"], "uploaded_by": "USER"},
        files={"file": ("test.jpg", img, "image/jpeg")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["dispute_id"] == dispute["id"]
    assert data["uploaded_by"] == "USER"
    assert data["file_type"] == "image/jpeg"
    assert data["storage_url"] is not None
    assert "id" in data


@pytest.mark.asyncio
async def test_upload_evidence_dispute_not_found(client: AsyncClient):
    img = _make_test_image()
    resp = await client.post(
        "/evidence/upload",
        data={"dispute_id": str(uuid.uuid4()), "uploaded_by": "USER"},
        files={"file": ("test.jpg", img, "image/jpeg")},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_evidence_unsupported_type(client: AsyncClient, dispute: dict):
    resp = await client.post(
        "/evidence/upload",
        data={"dispute_id": dispute["id"], "uploaded_by": "USER"},
        files={"file": ("test.gif", b"fakegif", "image/gif")},
    )
    assert resp.status_code == 400
    assert "Unsupported" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_upload_evidence_merchant_source(client: AsyncClient, dispute: dict):
    img = _make_test_image()
    resp = await client.post(
        "/evidence/upload",
        data={"dispute_id": dispute["id"], "uploaded_by": "MERCHANT"},
        files={"file": ("receipt.png", img, "image/png")},
    )
    assert resp.status_code == 201
    assert resp.json()["uploaded_by"] == "MERCHANT"


@pytest.mark.asyncio
async def test_get_evidence(client: AsyncClient, dispute: dict):
    img = _make_test_image()
    create_resp = await client.post(
        "/evidence/upload",
        data={"dispute_id": dispute["id"], "uploaded_by": "USER"},
        files={"file": ("test.jpg", img, "image/jpeg")},
    )
    evidence_id = create_resp.json()["id"]

    get_resp = await client.get(f"/evidence/{evidence_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == evidence_id


@pytest.mark.asyncio
async def test_ocr_service_parse_response():
    from app.services.ocr_vision import ocr_service

    result = ocr_service._parse_response(
        '{"invoice_number": "INV-001", "total_amount": 100.50}'
    )
    assert result["invoice_number"] == "INV-001"
    assert result["total_amount"] == 100.50


@pytest.mark.asyncio
async def test_ocr_service_parse_response_with_code_block():
    from app.services.ocr_vision import ocr_service

    result = ocr_service._parse_response(
        '```json\n{"invoice_number": "INV-002"}\n```'
    )
    assert result["invoice_number"] == "INV-002"


@pytest.mark.asyncio
async def test_ocr_service_no_key_returns_error():
    import os

    from app.services.ocr_vision import OCRVisionService

    svc = OCRVisionService()
    svc.client = None
    result = svc.run_ocr(b"fakebytes")
    assert "error" in result
    assert result["invoice_number"] is None

    result = svc.run_vision_analysis(b"fakebytes")
    assert "error" in result
    assert result["defects_detected"] is False


@pytest.mark.asyncio
async def test_evidence_dispute_includes_analysis_fields(client: AsyncClient, dispute: dict):
    img = _make_test_image()
    resp = await client.post(
        "/evidence/upload",
        data={"dispute_id": dispute["id"], "uploaded_by": "USER"},
        files={"file": ("test.jpg", img, "image/jpeg")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "ocr_extracted_json" in data
    assert "ai_vision_analysis" in data


@pytest.mark.asyncio
async def test_get_dispute_includes_evidence(client: AsyncClient, dispute: dict, user: dict, merchant: dict):
    img = _make_test_image()
    await client.post(
        "/evidence/upload",
        data={"dispute_id": dispute["id"], "uploaded_by": "USER"},
        files={"file": ("test.jpg", img, "image/jpeg")},
    )

    get_resp = await client.get(f"/disputes/{dispute['id']}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert len(data["evidence"]) >= 1
    assert data["evidence"][0]["file_type"] == "image/jpeg"
