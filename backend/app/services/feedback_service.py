"""Feedback learning service for OCR model improvement."""

import json
import csv
import io
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.correction import Correction
from app.models.ocr_result import OCRResult
from app.models.document import Document


class FeedbackService:
    """Service for building training datasets from OCR corrections."""

    @staticmethod
    async def get_training_pairs(
        db: AsyncSession,
        limit: int = 1000,
        min_text_length: int = 10,
    ) -> List[dict]:
        """
        Get OCR original → corrected text pairs for model training.
        Only includes corrections where the text has actually changed.
        """
        query = (
            select(Correction, OCRResult)
            .join(OCRResult, Correction.ocr_result_id == OCRResult.id)
            .where(
                Correction.original_text.isnot(None),
                Correction.corrected_text.isnot(None),
                func.length(Correction.original_text) >= min_text_length,
            )
            .order_by(Correction.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(query)
        rows = result.all()

        pairs = []
        for correction, ocr_result in rows:
            if correction.original_text != correction.corrected_text:
                pairs.append(
                    {
                        "id": str(correction.id),
                        "document_id": str(ocr_result.document_id),
                        "page_number": ocr_result.page_number,
                        "original_text": correction.original_text,
                        "corrected_text": correction.corrected_text,
                        "confidence_score": ocr_result.confidence_score,
                        "language": ocr_result.language,
                        "version": correction.version,
                        "created_at": correction.created_at.isoformat(),
                    }
                )

        return pairs

    @staticmethod
    async def export_dataset_csv(db: AsyncSession, limit: int = 10000) -> str:
        """Export training pairs as CSV string."""
        pairs = await FeedbackService.get_training_pairs(db, limit=limit)

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id",
                "document_id",
                "page_number",
                "original_text",
                "corrected_text",
                "confidence_score",
                "language",
                "version",
                "created_at",
            ],
        )
        writer.writeheader()
        for pair in pairs:
            writer.writerow(pair)

        return output.getvalue()

    @staticmethod
    async def export_dataset_json(db: AsyncSession, limit: int = 10000) -> str:
        """Export training pairs as JSON string."""
        pairs = await FeedbackService.get_training_pairs(db, limit=limit)
        return json.dumps(pairs, ensure_ascii=False, indent=2)

    @staticmethod
    async def get_accuracy_stats(db: AsyncSession) -> dict:
        """Get OCR accuracy statistics based on corrections."""
        # Total documents processed
        doc_count = await db.execute(
            select(func.count(Document.id)).where(Document.status == "processed")
        )
        total_processed = doc_count.scalar() or 0

        # Total OCR results
        ocr_count = await db.execute(
            select(func.count(OCRResult.id)).where(OCRResult.status == "completed")
        )
        total_ocr = ocr_count.scalar() or 0

        # Average confidence
        avg_conf = await db.execute(
            select(func.avg(OCRResult.confidence_score)).where(
                OCRResult.status == "completed"
            )
        )
        average_confidence = avg_conf.scalar() or 0

        # Total corrections
        corr_count = await db.execute(select(func.count(Correction.id)))
        total_corrections = corr_count.scalar() or 0

        # Corrected pages (unique OCR results with corrections)
        corrected_count = await db.execute(
            select(func.count(func.distinct(Correction.ocr_result_id)))
        )
        corrected_pages = corrected_count.scalar() or 0

        # Confidence distribution
        confidence_buckets = {}
        for low, high, label in [
            (0, 30, "low (0-30%)"),
            (30, 60, "medium (30-60%)"),
            (60, 80, "good (60-80%)"),
            (80, 100, "excellent (80-100%)"),
        ]:
            bucket_count = await db.execute(
                select(func.count(OCRResult.id)).where(
                    OCRResult.status == "completed",
                    OCRResult.confidence_score >= low,
                    OCRResult.confidence_score < high,
                )
            )
            confidence_buckets[label] = bucket_count.scalar() or 0

        return {
            "total_documents_processed": total_processed,
            "total_ocr_pages": total_ocr,
            "average_confidence": round(average_confidence, 2),
            "total_corrections": total_corrections,
            "corrected_pages": corrected_pages,
            "correction_rate": (
                round(corrected_pages / total_ocr * 100, 2) if total_ocr > 0 else 0
            ),
            "confidence_distribution": confidence_buckets,
        }
