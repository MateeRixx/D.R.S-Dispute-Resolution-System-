from decimal import Decimal

from app.services.reasoning import _deterministic_fallback, _parse_json, build_prompt


def test_build_prompt_includes_all_fields():
    prompt = build_prompt(
        evidence_summary="- Evidence from USER (image/jpeg): Invoice: Acme Corp",
        merchant_score=10,
        user_score=15,
        rules_triggered=[{"rule": "defects_detected", "points": 15, "awarded_to": "USER"}],
        user_narrative="Item arrived damaged",
        merchant_policy="30-day return policy",
        reason_code="ITEM_DEFECTIVE",
        amount=Decimal("4999.00"),
        currency="INR",
    )
    assert "Acme Corp" in prompt
    assert "defects_detected" in prompt
    assert "Item arrived damaged" in prompt
    assert "30-day return policy" in prompt
    assert "ITEM_DEFECTIVE" in prompt
    assert "4999.00" in prompt
    assert "INR" in prompt


def test_build_prompt_scrubs_pii():
    prompt = build_prompt(
        evidence_summary="No evidence",
        merchant_score=0,
        user_score=0,
        rules_triggered=[],
        user_narrative="Call me at 9876543210 or email test@example.com",
        merchant_policy=None,
        reason_code="ITEM_NOT_RECEIVED",
        amount=Decimal("1000.00"),
        currency="INR",
    )
    assert "[REDACTED_PHONE]" in prompt
    assert "[REDACTED_EMAIL]" in prompt
    assert "9876543210" not in prompt
    assert "test@example.com" not in prompt


def test_deterministic_fallback_user_wins():
    result = _deterministic_fallback(merchant_score=0, user_score=25)
    assert result["verdict"] == "REFUND_USER"
    assert result["confidence_score"] == 0.75


def test_deterministic_fallback_merchant_wins():
    result = _deterministic_fallback(merchant_score=25, user_score=0)
    assert result["verdict"] == "REJECT_CLAIM"
    assert result["confidence_score"] == 0.75


def test_deterministic_fallback_partial():
    result = _deterministic_fallback(merchant_score=10, user_score=15)
    assert result["verdict"] == "PARTIAL_REFUND"
    assert result["confidence_score"] == 0.60


def test_deterministic_fallback_inconclusive():
    result = _deterministic_fallback(merchant_score=0, user_score=0)
    assert result["verdict"] == "NEEDS_HUMAN_INTERVENTION"
    assert result["confidence_score"] == 0.50


def test_parse_json_clean():
    result = _parse_json('{"verdict": "REFUND_USER", "confidence_score": 0.85}')
    assert result["verdict"] == "REFUND_USER"
    assert result["confidence_score"] == 0.85


def test_parse_json_with_code_fence():
    result = _parse_json('```json\n{"verdict": "REJECT_CLAIM"}\n```')
    assert result["verdict"] == "REJECT_CLAIM"


def test_parse_json_invalid():
    result = _parse_json("not json at all")
    assert result is None


def test_evidence_summary_building():
    from app.models.dispute_models import Evidence
    from app.models.dispute_models import EvidenceSource as ES
    from app.services.adjudication import _build_evidence_summary

    ev = Evidence(
        dispute_id=None,
        uploaded_by=ES.USER,
        file_type="image/jpeg",
        storage_url="/tmp/test.jpg",
        ocr_extracted_json={"vendor_name": "Acme", "total_amount": 4999.00, "line_items": [{"desc": "phone"}]},
        ai_vision_analysis={"defects_detected": True, "defect_regions": [{"label": "cracked_screen"}]},
    )
    summary = _build_evidence_summary([ev])
    assert "USER" in summary
    assert "Acme" in summary
    assert "cracked_screen" in summary


def test_evidence_summary_empty():
    from app.services.adjudication import _build_evidence_summary
    assert _build_evidence_summary([]) == "No evidence uploaded."
