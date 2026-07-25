from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.dispute_models import Merchant
from app.schemas.dispute_schemas import MerchantCreate, MerchantResponse

router = APIRouter(prefix="/merchants", tags=["Merchants"])


@router.post("/", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
async def create_merchant(payload: MerchantCreate, db: AsyncSession = Depends(get_db)):
    merchant = Merchant(
        business_name=payload.business_name,
        shopify_domain=payload.shopify_domain,
        return_policy_url=payload.return_policy_url,
    )
    db.add(merchant)
    await db.flush()
    await db.refresh(merchant)
    return merchant
