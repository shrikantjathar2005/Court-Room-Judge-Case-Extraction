"""Correction API routes."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.correction import (
    CorrectionCreate,
    CorrectionResponse,
    CorrectionHistoryResponse,
)
from app.services.correction_service import CorrectionService
from app.middleware.auth_middleware import get_current_user, require_reviewer
from app.models.user import User

router = APIRouter(prefix="/api/corrections", tags=["Corrections"])


@router.post("/{ocr_result_id}", response_model=CorrectionResponse, status_code=201)
async def submit_correction(
    ocr_result_id: UUID,
    correction_data: CorrectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a text correction for an OCR result."""
    return await CorrectionService.create_correction(
        db, ocr_result_id, correction_data.corrected_text, current_user.id
    )


@router.get("/{ocr_result_id}/history", response_model=CorrectionHistoryResponse)
async def get_correction_history(
    ocr_result_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get correction history for an OCR result."""
    return await CorrectionService.get_correction_history(db, ocr_result_id)


@router.get("/pending/review")
async def get_pending_reviews(
    min_confidence: float = Query(0.0, ge=0),
    max_confidence: float = Query(70.0, le=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer),
):
    """Get OCR results pending review (sorted by lowest confidence)."""
    return await CorrectionService.get_pending_reviews(
        db,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        page=page,
        page_size=page_size,
    )
