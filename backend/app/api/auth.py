from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.models.dispute_models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    role: str = "customer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str
    merchant_id: Optional[str] = None


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(full_name=payload.email.split("@")[0], email=payload.email)
        db.add(user)
        await db.flush()
        await db.refresh(user)

    token = create_access_token(sub=str(user.id), role=payload.role)
    return LoginResponse(
        access_token=token,
        user_id=str(user.id),
        role=payload.role,
        full_name=user.full_name,
        merchant_id=str(user.merchant_id) if user.merchant_id else None,
    )
