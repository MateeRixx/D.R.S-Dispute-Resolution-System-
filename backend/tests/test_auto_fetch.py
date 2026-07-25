import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dispute_models import AutoFetchedLogs, Evidence, EvidenceSource
from app.services.adjudication import ScoreResult, _build_data_dict, calculate_scores
from app.services.auto_fetch import (
    fetch_razorpay,
    fetch_shiprocket,
    fetch_shopify,
    run_auto_fetch,
)


@pytest.mark.asyncio
async def test_fetch_razorpay_success():
    result = await fetch_razorpay("TXN-001")
    assert result["status"] == "CAPTURED"


@pytest.mark.asyncio
async def test_fetch_shopify_success():
    result = await fetch_shopify("ORD-001")
    assert result["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_fetch_shiprocket_success():
    result = await fetch_shiprocket("AWB-001")
    assert result["status"] == "DELIVERED"
    assert result["digital_signature"] == "PRESENT"


@pytest.mark.asyncio
async def test_auto_fetch_updates_logs(client: AsyncClient, user: dict, merchant: dict, db_session: AsyncSession):
    resp = await client.post("/disputes/", json={
        "transaction_id": "TXN-AF-001",
        "user_id": user["id"],
        "merchant_id": merchant["id"],
        "amount": "1000.00",
        "currency": "INR",
        "reason_code": "ITEM_NOT_RECEIVED",
    })
    assert resp.status_code == 201
    dispute_id = resp.json()["id"]

    await run_auto_fetch(dispute_id, "TXN-AF-001", "ORD-AF-001", "AWB-AF-001", db=db_session)

    get_resp = await client.get(f"/disputes/{dispute_id}")
    data = get_resp.json()
    assert data["auto_fetched_logs"] is not None
    assert data["auto_fetched_logs"]["razorpay_payload"]["status"] == "CAPTURED"
    assert data["auto_fetched_logs"]["shopify_payload"]["status"] == "COMPLETED"
    assert data["auto_fetched_logs"]["shiprocket_payload"]["status"] == "DELIVERED"
    assert data["status"] == "EVIDENCE_GATHERING"


@pytest.mark.asyncio
async def test_auto_fetch_timeout_handling():
    result = {"status": "FAILED", "error": "TIMEOUT"}
    assert result["status"] == "FAILED"
    assert result["error"] == "TIMEOUT"


def test_calculate_scores_empty_data():
    result = calculate_scores({})
    assert isinstance(result, ScoreResult)
    assert result.merchant_score == 0
    assert result.user_score == 0
    assert len(result.rules_triggered) == 0


def test_calculate_scores_merchant_wins():
    data = {
        "razorpay": {"status": "CAPTURED"},
        "shopify": {"status": "COMPLETED", "refund_policy_violated": False},
        "shiprocket": {"status": "DELIVERED", "digital_signature": "PRESENT"},
        "vision": {"defects_detected": False, "defect_regions": []},
    }
    result = calculate_scores(data)
    assert result.merchant_score == 25
    assert result.user_score == 0
    assert len(result.rules_triggered) == 2


def test_calculate_scores_user_wins():
    data = {
        "razorpay": {"status": "FAILED"},
        "shopify": {"status": "COMPLETED", "refund_policy_violated": True},
        "shiprocket": {"status": "DELIVERED", "digital_signature": "PRESENT"},
        "vision": {"defects_detected": True, "defect_regions": [{"label": "cracked_screen"}]},
    }
    result = calculate_scores(data)
    assert result.merchant_score == 25
    assert result.user_score == 45
    assert len(result.rules_triggered) == 5


def test_build_data_dict_with_missing_logs():
    data = _build_data_dict(None, [])
    assert data["razorpay"] == {}
    assert data["shopify"] == {}
    assert data["shiprocket"] == {}
    assert data["vision"]["defects_detected"] is False


def test_build_data_dict_with_evidence():
    ev = Evidence(
        dispute_id=None,
        uploaded_by=EvidenceSource.USER,
        file_type="image/jpeg",
        storage_url="/tmp/test.jpg",
        ai_vision_analysis={"defects_detected": True, "defect_regions": [{"label": "cracked_screen"}]},
    )
    data = _build_data_dict(None, [ev])
    assert data["vision"]["defects_detected"] is True


def test_calculate_scores_partial_data():
    data = {
        "razorpay": {"status": "FAILED"},
        "shopify": {},
        "shiprocket": {},
        "vision": {"defects_detected": False},
    }
    result = calculate_scores(data)
    assert result.user_score == 20
    assert result.merchant_score == 0
    assert len(result.rules_triggered) == 1
    assert result.rules_triggered[0]["rule"] == "razorpay_failed"
