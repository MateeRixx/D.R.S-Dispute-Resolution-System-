import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dispute_models import (
    AuditTrail,
    AutoFetchedLogs,
    Dispute,
    DisputeReasonCode,
    DisputeStatus,
    Evidence,
    EvidenceSource,
    Merchant,
    User,
    VerdictType,
)

logger = logging.getLogger(__name__)


async def seed_demo_data(db: AsyncSession):
    existing = await db.execute(select(User).where(User.email == "alice@example.com"))
    user = existing.scalar_one_or_none()
    if not user:
        user = User(full_name="Alice", email="alice@example.com")
        db.add(user)
        await db.flush()
        logger.info("Created demo user: alice@example.com")

    existing = await db.execute(select(Merchant).where(Merchant.business_name == "Acme Store"))
    merchant = existing.scalar_one_or_none()
    if not merchant:
        merchant = Merchant(
            business_name="Acme Store",
            shopify_domain="acme-store.myshopify.com",
            return_policy_url="https://acme-store.com/returns",
        )
        db.add(merchant)
        await db.flush()
        logger.info("Created demo merchant: Acme Store")

    existing_m = await db.execute(select(User).where(User.email == "merchant@acme.com"))
    merchant_user = existing_m.scalar_one_or_none()
    if not merchant_user:
        merchant_user = User(full_name="Acme Merchant", email="merchant@acme.com", merchant_id=merchant.id)
        db.add(merchant_user)
        await db.flush()
        logger.info("Created merchant user: merchant@acme.com")
    elif not merchant_user.merchant_id:
        merchant_user.merchant_id = merchant.id
        await db.flush()
        logger.info("Linked merchant@acme.com to Acme Store")

    existing = await db.execute(
        select(Dispute).where(Dispute.transaction_id == "TXN-DEMO-001")
    )
    dispute = existing.scalar_one_or_none()
    if not dispute:
        dispute = Dispute(
            transaction_id="TXN-DEMO-001",
            user_id=user.id,
            merchant_id=merchant.id,
            amount=Decimal("4999.00"),
            currency="INR",
            reason_code=DisputeReasonCode.ITEM_DEFECTIVE,
            user_narrative="Received a smartphone with a cracked screen. The packaging was intact but the screen was shattered.",
            status=DisputeStatus.DECISION_RENDERED,
            verdict=VerdictType.REFUND_USER,
            confidence_score=Decimal("0.88"),
            verdict_summary="User evidence (photo of cracked screen) combined with delivery confirmation shows item was received but defective. Merchant return policy allows returns within 15 days. Evidence strongly favours the user.",
        )
        db.add(dispute)
        await db.flush()

        audit_entries = [
            AuditTrail(dispute_id=dispute.id, action_taken="DISPUTE_CREATED", performed_by=str(user.id)),
            AuditTrail(dispute_id=dispute.id, action_taken="AUTO_FETCH_COMPLETED", performed_by="SYSTEM_AGENT",
                       metadata_json={"razorpay": "CAPTURED", "shopify": "COMPLETED", "shiprocket": "DELIVERED"}),
            AuditTrail(dispute_id=dispute.id, action_taken="EVIDENCE_UPLOADED", performed_by=str(user.id)),
            AuditTrail(dispute_id=dispute.id, action_taken="SCORING_COMPLETED", performed_by="SYSTEM_AGENT",
                       metadata_json={"merchant_score": 10, "user_score": 25, "rules": "defects_detected, shiprocket_delivered"}),
            AuditTrail(dispute_id=dispute.id, action_taken="DECISION_RENDERED", performed_by="SYSTEM_AGENT",
                       metadata_json={"verdict": "REFUND_USER", "confidence_score": 0.88}),
        ]
        for a in audit_entries:
            db.add(a)

        auto_logs = AutoFetchedLogs(
            dispute_id=dispute.id,
            razorpay_payload={"status": "CAPTURED", "transaction_id": "pay_demo_001", "amount": 4999.00, "currency": "INR"},
            shopify_payload={"status": "COMPLETED", "order_id": "ORD-DEMO-001", "refund_policy_violated": False, "refund_policy_excerpt": "Returns accepted within 15 days of delivery."},
            shiprocket_payload={"status": "DELIVERED", "awb": "AWB-DEMO-001", "delivered_at": "2026-07-22T14:30:00Z", "digital_signature": "PRESENT", "location_scan": "Mumbai, Maharashtra"},
        )
        db.add(auto_logs)

        evidence = Evidence(
            dispute_id=dispute.id,
            uploaded_by=EvidenceSource.USER,
            file_type="image/jpeg",
            storage_url="uploads/demo_cracked_screen.jpg",
            ocr_extracted_json={"invoice_number": "INV-DEMO-001", "vendor_name": "Acme Store", "total_amount": 4999.00, "currency": "INR", "line_items": [{"description": "Smartphone", "quantity": 1, "unit_price": 4999.00, "total": 4999.00}]},
            ai_vision_analysis={"defects_detected": True, "defect_regions": [{"label": "cracked_screen", "confidence": 0.95, "bbox": [50, 100, 200, 300]}], "overall_condition": "Screen has visible crack lines across the top-left quadrant"},
        )
        db.add(evidence)

        await db.commit()
        logger.info("Created demo dispute: TXN-DEMO-001 with verdict REFUND_USER")
    else:
        logger.info("Demo dispute already exists")

    return {"user": {"id": str(user.id), "email": user.email}, "merchant": {"id": str(merchant.id), "business_name": merchant.business_name}}


async def main():
    from app.core.database import async_session_factory
    async with async_session_factory() as db:
        await seed_demo_data(db)
    print("Seeding complete.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
