import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.dispute_models import (
    AuditTrail,
    AutoFetchedLogs,
    Dispute,
    DisputeStatus,
)

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10


async def fetch_razorpay(transaction_id: str) -> dict:
    try:
        async with asyncio.timeout(TIMEOUT_SECONDS):
            logger.info("Razorpay fetch: %s", transaction_id)
            await asyncio.sleep(0.1)
            return {"status": "CAPTURED", "transaction_id": transaction_id, "amount": 4999.00, "currency": "INR"}
    except asyncio.TimeoutError:
        return {"status": "FAILED", "error": "TIMEOUT"}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


async def fetch_shopify(order_id: str) -> dict:
    try:
        async with asyncio.timeout(TIMEOUT_SECONDS):
            logger.info("Shopify fetch: %s", order_id)
            await asyncio.sleep(0.1)
            return {
                "status": "COMPLETED",
                "order_id": order_id,
                "items": [{"sku": "PHN-001", "name": "Smartphone"}],
                "refund_policy_violated": False,
                "refund_policy_excerpt": "Returns accepted within 15 days of delivery.",
            }
    except asyncio.TimeoutError:
        return {"status": "FAILED", "error": "TIMEOUT"}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


async def fetch_shiprocket(awb_number: str) -> dict:
    try:
        async with asyncio.timeout(TIMEOUT_SECONDS):
            logger.info("Shiprocket fetch: %s", awb_number)
            await asyncio.sleep(0.1)
            return {
                "status": "DELIVERED",
                "awb": awb_number,
                "delivered_at": "2026-07-20T14:30:00Z",
                "digital_signature": "PRESENT",
                "location_scan": "Mumbai, Maharashtra",
            }
    except asyncio.TimeoutError:
        return {"status": "FAILED", "error": "TIMEOUT"}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


async def run_auto_fetch(
    dispute_id,
    transaction_id: str,
    order_id: str,
    awb_number: Optional[str] = None,
    db: Optional[AsyncSession] = None,
):
    try:
        razorpay_result, shopify_result, shiprocket_result = await asyncio.gather(
            fetch_razorpay(transaction_id),
            fetch_shopify(order_id),
            fetch_shiprocket(awb_number or transaction_id),
        )
    except Exception as e:
        logger.error("Unexpected error in auto_fetch for dispute %s: %s", dispute_id, e)
        razorpay_result = {"status": "FAILED", "error": str(e)}
        shopify_result = {"status": "FAILED", "error": str(e)}
        shiprocket_result = {"status": "FAILED", "error": str(e)}

    if db is not None:
        await _persist(db, dispute_id, razorpay_result, shopify_result, shiprocket_result)
    else:
        async with async_session_factory() as session:
            await _persist(session, dispute_id, razorpay_result, shopify_result, shiprocket_result)


async def _persist(db, dispute_id, razorpay, shopify, shiprocket):
    try:
        result = await db.execute(select(AutoFetchedLogs).where(AutoFetchedLogs.dispute_id == dispute_id))
        logs = result.scalar_one_or_none()

        if logs:
            logs.razorpay_payload = razorpay
            logs.shopify_payload = shopify
            logs.shiprocket_payload = shiprocket
            logs.fetched_at = datetime.now(timezone.utc)
        else:
            logs = AutoFetchedLogs(
                dispute_id=dispute_id,
                razorpay_payload=razorpay,
                shopify_payload=shopify,
                shiprocket_payload=shiprocket,
            )
            db.add(logs)

        dispute_result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
        dispute = dispute_result.scalar_one()
        dispute.status = DisputeStatus.EVIDENCE_GATHERING

        audit = AuditTrail(
            dispute_id=dispute_id,
            action_taken="AUTO_FETCH_COMPLETED",
            performed_by="SYSTEM_AGENT",
            metadata_json={
                "razorpay": razorpay.get("status"),
                "shopify": shopify.get("status"),
                "shiprocket": shiprocket.get("status"),
            },
        )
        db.add(audit)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error("Failed to persist auto_fetch results for dispute %s: %s", dispute_id, e)
