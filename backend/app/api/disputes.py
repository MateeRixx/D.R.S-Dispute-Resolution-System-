from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.dispute_models import Dispute, DisputeStatus, AuditTrail
from app.schemas.dispute_schemas import DisputeCreate, DisputeResponse

router = APIRouter(prefix="/disputes", tags=["Disputes"])


@router.post("/", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def create_dispute(payload: DisputeCreate, db: AsyncSession = Depends(get_db)):
    try:
        dispute = Dispute(
            transaction_id=payload.transaction_id,
            user_id=payload.user_id,
            merchant_id=payload.merchant_id,
            amount=payload.amount,
            currency=payload.currency,
            reason_code=payload.reason_code,
            user_narrative=payload.user_narrative,
            status=DisputeStatus.INITIATED,
        )
        db.add(dispute)
        await db.flush()

        audit = AuditTrail(
            dispute_id=dispute.id,
            action_taken="DISPUTE_CREATED",
            performed_by=str(payload.user_id),
            metadata_json={"reason_code": payload.reason_code.value, "amount": str(payload.amount)},
        )
        db.add(audit)

        await db.refresh(dispute)
        result = await db.execute(
            select(Dispute)
            .where(Dispute.id == dispute.id)
            .options(
                selectinload(Dispute.evidence),
                selectinload(Dispute.auto_fetched_logs),
                selectinload(Dispute.audit_trail),
            )
        )
        return result.scalar_one()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid reference: user_id or merchant_id does not exist.",
        )


@router.get("/{dispute_id}", response_model=DisputeResponse)
async def get_dispute(dispute_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Dispute)
        .where(Dispute.id == dispute_id)
        .options(
            selectinload(Dispute.evidence),
            selectinload(Dispute.auto_fetched_logs),
            selectinload(Dispute.audit_trail),
        )
    )
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")
    return dispute
