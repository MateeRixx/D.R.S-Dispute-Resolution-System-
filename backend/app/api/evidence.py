import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.dispute_models import Dispute, Evidence, EvidenceSource
from app.schemas.dispute_schemas import EvidenceResponse
from app.services.ocr_vision import ocr_service

router = APIRouter(prefix="/evidence", tags=["Evidence"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}


@router.post("/upload", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    dispute_id: uuid.UUID = Form(...),
    uploaded_by: EvidenceSource = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    dispute = await db.get(Dispute, dispute_id)
    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_TYPES}",
        )

    file_id = uuid.uuid4()
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "application/pdf": ".pdf"}[file.content_type]
    filename = f"{file_id}{ext}"
    filepath = UPLOAD_DIR / filename

    content = await file.read()
    filepath.write_bytes(content)

    ocr_result = None
    vision_result = None

    if file.content_type != "application/pdf" and ocr_service.is_available():
        try:
            if file.content_type in ("image/jpeg", "image/png", "image/webp"):
                vision_result = ocr_service.run_vision_analysis(content)
                ocr_result = ocr_service.run_ocr(content)
        except Exception:
            pass

    evidence = Evidence(
        dispute_id=dispute_id,
        uploaded_by=uploaded_by,
        file_type=file.content_type,
        storage_url=str(filepath),
        ocr_extracted_json=ocr_result,
        ai_vision_analysis=vision_result,
    )
    db.add(evidence)
    await db.flush()
    await db.refresh(evidence)
    return evidence


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(evidence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Evidence).where(Evidence.id == evidence_id).options(selectinload(Evidence.dispute))
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    return evidence
