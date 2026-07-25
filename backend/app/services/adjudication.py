import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import async_session_factory
from app.models.dispute_models import (
    AuditTrail,
    AutoFetchedLogs,
    Dispute,
    DisputeStatus,
    Evidence,
    VerdictType,
)
from app.services.reasoning import generate_verdict

logger = logging.getLogger(__name__)


@dataclass
class ScoreResult:
    merchant_score: int
    user_score: int
    rules_triggered: list[dict]


SCORING_RULES = [
    ("shiprocket_delivered", lambda d: d.get("shiprocket", {}).get("status") == "DELIVERED", +10, "MERCHANT"),
    ("shiprocket_signature", lambda d: d.get("shiprocket", {}).get("digital_signature") == "PRESENT", +15, "MERCHANT"),
    ("defects_detected", lambda d: d.get("vision", {}).get("defects_detected") is True, +15, "USER"),
    ("refund_policy_violated", lambda d: d.get("shopify", {}).get("refund_policy_violated") is True, +10, "USER"),
    ("razorpay_failed", lambda d: d.get("razorpay", {}).get("status") == "FAILED", +20, "USER"),
]


def _build_data_dict(
    auto_logs: Optional[AutoFetchedLogs],
    evidence_list: list[Evidence],
) -> dict:
    razorpay = {}
    shopify = {}
    shiprocket = {}
    vision = {"defects_detected": False, "defect_regions": []}

    if auto_logs:
        if auto_logs.razorpay_payload:
            razorpay = auto_logs.razorpay_payload
        if auto_logs.shopify_payload:
            shopify = auto_logs.shopify_payload
        if auto_logs.shiprocket_payload:
            shiprocket = auto_logs.shiprocket_payload

    for ev in evidence_list:
        if ev.ai_vision_analysis and ev.ai_vision_analysis.get("defects_detected"):
            vision = ev.ai_vision_analysis
            break

    return {
        "razorpay": razorpay,
        "shopify": shopify,
        "shiprocket": shiprocket,
        "vision": vision,
    }


def _build_evidence_summary(evidence_list: list[Evidence]) -> str:
    if not evidence_list:
        return "No evidence uploaded."

    parts = []
    for ev in evidence_list:
        source = ev.uploaded_by.value if ev.uploaded_by else "UNKNOWN"
        ftype = ev.file_type or "unknown"
        summary = f"- Evidence from {source} ({ftype})"

        if ev.ocr_extracted_json and "error" not in ev.ocr_extracted_json:
            ocr = ev.ocr_extracted_json
            vendor = ocr.get("vendor_name") or "unknown vendor"
            total = ocr.get("total_amount") or "unknown amount"
            items = len(ocr.get("line_items", []))
            summary += f" — Invoice: {vendor}, {total}, {items} line item(s)"

        if ev.ai_vision_analysis:
            vis = ev.ai_vision_analysis
            if vis.get("defects_detected"):
                regions = ", ".join(r.get("label", "unknown") for r in vis.get("defect_regions", []))
                summary += f" — Defects: {regions}"
            elif "error" not in vis:
                summary += " — No defects detected"

        parts.append(summary)

    return "\n".join(parts) if parts else "No evidence summary available."


def calculate_scores(data: dict) -> ScoreResult:
    merchant_score = 0
    user_score = 0
    rules_triggered = []

    for rule_id, condition_fn, points, awarded_to in SCORING_RULES:
        try:
            if condition_fn(data):
                if awarded_to == "MERCHANT":
                    merchant_score += points
                else:
                    user_score += points
                rules_triggered.append({"rule": rule_id, "points": points, "awarded_to": awarded_to})
        except Exception as e:
            logger.warning("Rule %s evaluation failed: %s", rule_id, e)

    return ScoreResult(
        merchant_score=merchant_score,
        user_score=user_score,
        rules_triggered=rules_triggered,
    )


async def run_adjudication(dispute_id, db: Optional[AsyncSession] = None):
    if db is None:
        async with async_session_factory() as session:
            await _adjudicate(session, dispute_id)
    else:
        await _adjudicate(db, dispute_id)


async def _adjudicate(db: AsyncSession, dispute_id):
    try:
        result = await db.execute(
            select(Dispute)
            .where(Dispute.id == dispute_id)
            .options(
                selectinload(Dispute.auto_fetched_logs),
                selectinload(Dispute.evidence),
                selectinload(Dispute.merchant),
            )
        )
        dispute = result.scalar_one_or_none()
        if not dispute:
            logger.warning("Dispute %s not found for adjudication", dispute_id)
            return

        data = _build_data_dict(dispute.auto_fetched_logs, dispute.evidence)
        score = calculate_scores(data)

        evidence_summary = _build_evidence_summary(dispute.evidence)

        verdict_result = await generate_verdict(
            evidence_summary=evidence_summary,
            merchant_score=score.merchant_score,
            user_score=score.user_score,
            rules_triggered=score.rules_triggered,
            user_narrative=dispute.user_narrative,
            merchant_policy=dispute.merchant.return_policy_url if dispute.merchant else None,
            reason_code=dispute.reason_code.value if dispute.reason_code else "",
            amount=dispute.amount,
            currency=dispute.currency,
        )

        verdict_str = verdict_result.get("verdict", "NEEDS_HUMAN_INTERVENTION")
        confidence = verdict_result.get("confidence_score", 0.5)
        reasoning = verdict_result.get("reasoning_summary", "")

        try:
            dispute.verdict = VerdictType(verdict_str)
        except ValueError:
            dispute.verdict = VerdictType.NEEDS_HUMAN_INTERVENTION

        dispute.confidence_score = Decimal(str(confidence))
        dispute.verdict_summary = reasoning
        dispute.status = DisputeStatus.DECISION_RENDERED

        audit = AuditTrail(
            dispute_id=dispute_id,
            action_taken="DECISION_RENDERED",
            performed_by="SYSTEM_AGENT",
            metadata_json={
                "verdict": dispute.verdict.value,
                "confidence_score": confidence,
                "reasoning_summary": reasoning,
                "merchant_score": score.merchant_score,
                "user_score": score.user_score,
                "rules_triggered": score.rules_triggered,
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Adjudication for dispute %s — Verdict: %s (confidence: %.2f)",
            dispute_id,
            dispute.verdict.value,
            confidence,
        )
    except Exception as e:
        await db.rollback()
        logger.error("Adjudication failed for dispute %s: %s", dispute_id, e)
