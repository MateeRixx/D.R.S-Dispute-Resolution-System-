from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.dispute_models import DisputeStatus, DisputeReasonCode, VerdictType, EvidenceSource


class UserCreate(BaseModel):
    full_name: str = Field(..., max_length=255)
    email: str = Field(..., max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone_number: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MerchantCreate(BaseModel):
    business_name: str = Field(..., max_length=255)
    shopify_domain: Optional[str] = Field(None, max_length=255)
    return_policy_url: Optional[str] = None


class MerchantResponse(BaseModel):
    id: UUID
    business_name: str
    shopify_domain: Optional[str]
    return_policy_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DisputeCreate(BaseModel):
    transaction_id: str = Field(..., max_length=255)
    user_id: UUID
    merchant_id: UUID
    amount: Decimal = Field(..., max_digits=12, decimal_places=2)
    currency: str = Field(default="INR", max_length=3)
    reason_code: DisputeReasonCode
    user_narrative: Optional[str] = None


class EvidenceResponse(BaseModel):
    id: UUID
    dispute_id: UUID
    uploaded_by: EvidenceSource
    file_type: str
    storage_url: str
    ocr_extracted_json: Optional[dict]
    ai_vision_analysis: Optional[dict]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class AutoFetchedLogsResponse(BaseModel):
    id: UUID
    dispute_id: UUID
    razorpay_payload: Optional[dict]
    shopify_payload: Optional[dict]
    shiprocket_payload: Optional[dict]
    fetched_at: datetime

    model_config = {"from_attributes": True}


class AuditTrailResponse(BaseModel):
    id: UUID
    dispute_id: UUID
    action_taken: str
    performed_by: str
    metadata_json: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DisputeResponse(BaseModel):
    id: UUID
    transaction_id: str
    user_id: UUID
    merchant_id: UUID
    amount: Decimal
    currency: str
    reason_code: DisputeReasonCode
    status: DisputeStatus
    user_narrative: Optional[str]
    verdict: Optional[VerdictType]
    confidence_score: Optional[Decimal]
    verdict_summary: Optional[str]
    created_at: datetime
    updated_at: datetime
    evidence: list[EvidenceResponse] = []
    auto_fetched_logs: Optional[AutoFetchedLogsResponse]
    audit_trail: list[AuditTrailResponse] = []

    model_config = {"from_attributes": True}
