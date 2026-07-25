import asyncio
import json
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import async_session_factory, get_db
from app.core.security import decode_token
from app.models.dispute_models import Dispute, DisputeStatus
from app.schemas.dispute_schemas import DisputeResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Portal"])


@router.get("/portal/disputes", response_model=list[DisputeResponse])
async def list_disputes(
    user_id: Optional[UUID] = Query(None),
    merchant_id: Optional[UUID] = Query(None),
    status_filter: Optional[DisputeStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Dispute).options(
        selectinload(Dispute.evidence),
        selectinload(Dispute.auto_fetched_logs),
        selectinload(Dispute.audit_trail),
    )

    if user_id:
        query = query.where(Dispute.user_id == user_id)
    if merchant_id:
        query = query.where(Dispute.merchant_id == merchant_id)
    if status_filter:
        query = query.where(Dispute.status == status_filter)

    query = query.order_by(Dispute.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/portal/disputes/{dispute_id}", response_model=DisputeResponse)
async def get_portal_dispute(dispute_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Dispute)
        .where(Dispute.id == dispute_id)
        .options(
            selectinload(Dispute.evidence),
            selectinload(Dispute.auto_fetched_logs),
            selectinload(Dispute.audit_trail),
            selectinload(Dispute.user),
            selectinload(Dispute.merchant),
        )
    )
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")
    return dispute


@router.get("/portal/disputes/{dispute_id}/events")
async def dispute_sse(
    dispute_id: UUID,
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    if token:
        decode_token(token)

    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")

    async def event_stream():
        last_status = None
        last_verdict = None
        while True:
            try:
                async with async_session_factory() as sse_db:
                    sse_result = await sse_db.execute(
                        select(Dispute)
                        .where(Dispute.id == dispute_id)
                        .options(
                            selectinload(Dispute.auto_fetched_logs),
                            selectinload(Dispute.audit_trail),
                        )
                    )
                    current = sse_result.scalar_one_or_none()
                    if not current:
                        yield f"event: error\ndata: {json.dumps({'message': 'Dispute not found'})}\n\n"
                        break

                    status_changed = current.status != last_status and last_status is not None
                    verdict_changed = current.verdict != last_verdict and last_verdict is not None

                    if status_changed or verdict_changed or last_status is None:
                        payload = {
                            "dispute_id": str(current.id),
                            "status": current.status.value if current.status else None,
                            "verdict": current.verdict.value if current.verdict else None,
                            "confidence_score": float(current.confidence_score) if current.confidence_score else None,
                            "verdict_summary": current.verdict_summary,
                            "auto_fetched_logs": {
                                "razorpay": (current.auto_fetched_logs.razorpay_payload.get("status") if current.auto_fetched_logs and current.auto_fetched_logs.razorpay_payload else None),
                                "shopify": (current.auto_fetched_logs.shopify_payload.get("status") if current.auto_fetched_logs and current.auto_fetched_logs.shopify_payload else None),
                                "shiprocket": (current.auto_fetched_logs.shiprocket_payload.get("status") if current.auto_fetched_logs and current.auto_fetched_logs.shiprocket_payload else None),
                            } if current.auto_fetched_logs else None,
                            "audit_trail": [
                                {"action": a.action_taken, "performed_by": a.performed_by, "created_at": a.created_at.isoformat() if a.created_at else None}
                                for a in (current.audit_trail or [])
                            ] if current.audit_trail else [],
                        }
                        yield f"event: dispute_update\ndata: {json.dumps(payload)}\n\n"
                        last_status = current.status
                        last_verdict = current.verdict

                    await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("SSE error for dispute %s: %s", dispute_id, e)
                yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
                await asyncio.sleep(5)

    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_stream(), media_type="text/event-stream")
