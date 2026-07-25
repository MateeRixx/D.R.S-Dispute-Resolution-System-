import hashlib
import hmac
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.dispute_models import AuditTrail, Dispute, DisputeStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/dispute-event")
async def webhook_dispute_event(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("X-DRS-Signature", "")
    secret = settings.webhook_secret

    if secret and not verify_signature(body, signature, secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

    event_type = data.get("event")
    transaction_id = data.get("transaction_id")

    if not event_type or not transaction_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing event or transaction_id")

    result = await db.execute(select(Dispute).where(Dispute.transaction_id == transaction_id))
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")

    audit = AuditTrail(
        dispute_id=dispute.id,
        action_taken=f"WEBHOOK_{event_type}",
        performed_by="EXTERNAL_SYSTEM",
        metadata_json={"event": event_type, "payload": data.get("payload", {})},
    )
    db.add(audit)

    if event_type == "PAYMENT_CONFIRMED":
        dispute.status = DisputeStatus.EVIDENCE_GATHERING
    elif event_type == "SHIPMENT_DELIVERED":
        dispute.status = DisputeStatus.EVIDENCE_GATHERING
    elif event_type == "MERCHANT_RESPONDED":
        dispute.status = DisputeStatus.UNDER_REVIEW

    await db.commit()
    return {"status": "received", "dispute_id": str(dispute.id)}
