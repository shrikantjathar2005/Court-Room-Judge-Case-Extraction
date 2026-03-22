"""Correction service for OCR text corrections."""

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from fastapi import HTTPException, status
from app.models.ocr_result import OCRResult
from app.models.correction import Correction


class CorrectionService:
    """Service for managing text corrections."""

    @staticmethod
    async def create_correction(
        db: AsyncSession,
        ocr_result_id: uuid.UUID,
        corrected_text: str,
        user_id: uuid.UUID,
    ) -> Correction:
        """Submit a correction for an OCR result."""
        # Get OCR result
        result = await db.execute(
            select(OCRResult).where(OCRResult.id == ocr_result_id)
        )
        ocr_result = result.scalar_one_or_none()

        if not ocr_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OCR result not found",
            )

        # Get current version number
        version_result = await db.execute(
            select(func.max(Correction.version))
            .where(Correction.ocr_result_id == ocr_result_id)
        )
        max_version = version_result.scalar() or 0

        # Create correction
        correction = Correction(
            ocr_result_id=ocr_result_id,
            original_text=ocr_result.raw_text,
            corrected_text=corrected_text,
            corrected_by=user_id,
            version=max_version + 1,
        )

        db.add(correction)
        await db.flush()
        await db.refresh(correction)
        return correction

    @staticmethod
    async def get_correction_history(
        db: AsyncSession, ocr_result_id: uuid.UUID
    ) -> dict:
        """Get all corrections for an OCR result."""
        results = await db.execute(
            select(Correction)
            .where(Correction.ocr_result_id == ocr_result_id)
            .order_by(desc(Correction.version))
        )
        corrections = results.scalars().all()

        return {
            "ocr_result_id": ocr_result_id,
            "corrections": corrections,
            "total_versions": len(corrections),
        }

    @staticmethod
    async def get_pending_reviews(
        db: AsyncSession,
        min_confidence: float = 0.0,
        max_confidence: float = 70.0,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get OCR results needing review (low confidence, no corrections)."""
        # Get OCR results with low confidence that haven't been corrected
        subquery = select(Correction.ocr_result_id).distinct()

        query = (
            select(OCRResult)
            .where(
                OCRResult.status == "completed",
                OCRResult.confidence_score >= min_confidence,
                OCRResult.confidence_score <= max_confidence,
                OCRResult.id.notin_(subquery),
            )
            .order_by(OCRResult.confidence_score.asc())
        )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        results = await db.execute(query)
        ocr_results = results.scalars().all()

        return {
            "results": ocr_results,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
