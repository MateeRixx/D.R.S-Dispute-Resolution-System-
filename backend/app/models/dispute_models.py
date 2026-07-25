import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, Enum, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

import enum


class DisputeStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    EVIDENCE_GATHERING = "EVIDENCE_GATHERING"
    UNDER_REVIEW = "UNDER_REVIEW"
    DECISION_RENDERED = "DECISION_RENDERED"
    CLOSED = "CLOSED"


class DisputeReasonCode(str, enum.Enum):
    ITEM_NOT_RECEIVED = "ITEM_NOT_RECEIVED"
    ITEM_DEFECTIVE = "ITEM_DEFECTIVE"
    INCORRECT_AMOUNT = "INCORRECT_AMOUNT"
    UNAUTHORIZED_TRANSACTION = "UNAUTHORIZED_TRANSACTION"
    SUBSCRIPTION_CANCELLED = "SUBSCRIPTION_CANCELLED"


class VerdictType(str, enum.Enum):
    REFUND_USER = "REFUND_USER"
    REJECT_CLAIM = "REJECT_CLAIM"
    PARTIAL_REFUND = "PARTIAL_REFUND"
    NEEDS_HUMAN_INTERVENTION = "NEEDS_HUMAN_INTERVENTION"


class EvidenceSource(str, enum.Enum):
    USER = "USER"
    MERCHANT = "MERCHANT"
    AUTO_API = "AUTO_API"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    disputes = relationship("Dispute", back_populates="user")


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_name = Column(String(255), nullable=False)
    shopify_domain = Column(String(255), nullable=True)
    api_key_hash = Column(String(255), nullable=True)
    return_policy_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    disputes = relationship("Dispute", back_populates="merchant")


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="INR")
    reason_code = Column(Enum(DisputeReasonCode), nullable=False)
    status = Column(Enum(DisputeStatus), default=DisputeStatus.INITIATED)
    user_narrative = Column(Text, nullable=True)
    verdict = Column(Enum(VerdictType), nullable=True)
    confidence_score = Column(DECIMAL(5, 2), nullable=True)
    verdict_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="disputes")
    merchant = relationship("Merchant", back_populates="disputes")
    evidence = relationship("Evidence", back_populates="dispute")
    auto_fetched_logs = relationship("AutoFetchedLogs", back_populates="dispute", uselist=False)
    audit_trail = relationship("AuditTrail", back_populates="dispute")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(Enum(EvidenceSource), nullable=False)
    file_type = Column(String(50), nullable=False)
    storage_url = Column(Text, nullable=False)
    ocr_extracted_json = Column(JSONB, nullable=True)
    ai_vision_analysis = Column(JSONB, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    dispute = relationship("Dispute", back_populates="evidence")


class AutoFetchedLogs(Base):
    __tablename__ = "auto_fetched_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), unique=True, nullable=False)
    razorpay_payload = Column(JSONB, nullable=True)
    shopify_payload = Column(JSONB, nullable=True)
    shiprocket_payload = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    dispute = relationship("Dispute", back_populates="auto_fetched_logs")


class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False)
    action_taken = Column(String(255), nullable=False)
    performed_by = Column(String(100), nullable=False)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    dispute = relationship("Dispute", back_populates="audit_trail")
