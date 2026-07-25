import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.dispute_models import Dispute, Merchant, VerdictType
from app.seed import seed_demo_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/bulk/re-adjudicate")
async def bulk_readjudicate(payload: dict, db: AsyncSession = Depends(get_db)):
    dispute_ids = payload.get("dispute_ids", [])
    if not dispute_ids:
        raise HTTPException(status_code=400, detail="No dispute_ids provided")

    from uuid import UUID

    from app.services.adjudication import run_adjudication

    results = []
    for did in dispute_ids:
        try:
            uid = UUID(did)
            await run_adjudication(uid, db)
            results.append({"dispute_id": did, "status": "re-adjudicated"})
        except Exception as e:
            results.append({"dispute_id": did, "status": "failed", "error": str(e)})
    await db.commit()
    return {"results": results}


@router.post("/bulk/export")
async def bulk_export(payload: dict, db: AsyncSession = Depends(get_db)):
    dispute_ids = payload.get("dispute_ids", [])
    from uuid import UUID

    if not dispute_ids:
        result = await db.execute(select(Dispute))
        disputes = result.scalars().all()
    else:
        result = await db.execute(
            select(Dispute).where(Dispute.id.in_([UUID(d) for d in dispute_ids]))
        )
        disputes = result.scalars().all()

    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "transaction_id", "reason_code", "status", "verdict", "confidence", "amount", "currency", "created_at"])
    for d in disputes:
        writer.writerow([str(d.id), d.transaction_id, d.reason_code.value if d.reason_code else "", d.status.value if d.status else "", d.verdict.value if d.verdict else "", float(d.confidence_score or 0), float(d.amount), d.currency, d.created_at.isoformat() if d.created_at else ""])
    return {"csv": output.getvalue()}


@router.get("/stats")
async def admin_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(func.count(Dispute.id)))
    total = result.scalar() or 0

    result = await db.execute(
        select(Dispute.status, func.count(Dispute.id)).group_by(Dispute.status)
    )
    by_status = {row[0].value if hasattr(row[0], "value") else row[0]: row[1] for row in result}

    result = await db.execute(
        select(Dispute.verdict, func.count(Dispute.id)).where(Dispute.verdict.isnot(None)).group_by(Dispute.verdict)
    )
    by_verdict = {row[0].value if hasattr(row[0], "value") else row[0]: row[1] for row in result}

    result = await db.execute(
        select(Dispute.reason_code, func.count(Dispute.id)).group_by(Dispute.reason_code)
    )
    by_reason = {row[0].value if hasattr(row[0], "value") else row[0]: row[1] for row in result}

    result = await db.execute(select(Merchant.business_name, func.count(Dispute.id)).join(Dispute, Dispute.merchant_id == Merchant.id, isouter=True).group_by(Merchant.business_name))
    by_merchant = {row[0]: row[1] for row in result}

    result = await db.execute(
        select(
            func.date_trunc("day", Dispute.created_at),
            func.count(Dispute.id),
        ).group_by(func.date_trunc("day", Dispute.created_at)).order_by(func.date_trunc("day", Dispute.created_at))
    )
    volume_over_time = [
        {"date": str(row[0]), "count": row[1]} for row in result
    ]

    result = await db.execute(
        select(func.avg(Dispute.confidence_score)).where(Dispute.confidence_score.isnot(None))
    )
    avg_confidence = float(result.scalar() or 0)

    resolved = sum(by_verdict.get(v.value if hasattr(v, "value") else v, 0) for v in [VerdictType.REFUND_USER, VerdictType.REJECT_CLAIM, VerdictType.PARTIAL_REFUND])
    resolution_rate = round(resolved / total * 100, 1) if total else 0

    return {
        "total_disputes": total,
        "by_status": by_status,
        "by_verdict": by_verdict,
        "by_reason_code": by_reason,
        "by_merchant": by_merchant,
        "volume_over_time": volume_over_time,
        "avg_confidence": round(avg_confidence, 2),
        "resolution_rate": resolution_rate,
    }


@router.post("/reset", status_code=status.HTTP_200_OK)
async def reset_demo(db: AsyncSession = Depends(get_db)):
    try:
        tables = [
            "audit_trail", "auto_fetched_logs", "evidence",
            "disputes", "merchants", "users",
        ]
        for table in tables:
            await db.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
        await db.commit()

        await seed_demo_data(db)

        return {"message": "Demo data reset successfully"}
    except Exception as e:
        await db.rollback()
        logger.error("Reset failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset failed: {str(e)}",
        )
