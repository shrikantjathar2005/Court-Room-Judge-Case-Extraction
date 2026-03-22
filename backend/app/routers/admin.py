"""Admin API routes."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.middleware.auth_middleware import require_admin
from app.models.user import User
from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.models.correction import Correction
from app.services.feedback_service import FeedbackService
from app.schemas.user import UserResponse, UserUpdate
from typing import List
from uuid import UUID

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get system-wide statistics."""
    # User count
    user_count = await db.execute(select(func.count(User.id)))
    total_users = user_count.scalar() or 0

    # Document counts by status
    doc_counts = {}
    for status in ["uploaded", "processing", "processed", "reviewed"]:
        count = await db.execute(
            select(func.count(Document.id)).where(Document.status == status)
        )
        doc_counts[status] = count.scalar() or 0

    total_docs = sum(doc_counts.values())

    # OCR stats
    ocr_count = await db.execute(
        select(func.count(OCRResult.id)).where(OCRResult.status == "completed")
    )
    total_ocr_pages = ocr_count.scalar() or 0

    avg_conf = await db.execute(
        select(func.avg(OCRResult.confidence_score)).where(
            OCRResult.status == "completed"
        )
    )
    avg_confidence = avg_conf.scalar() or 0

    # Correction count
    corr_count = await db.execute(select(func.count(Correction.id)))
    total_corrections = corr_count.scalar() or 0

    return {
        "total_users": total_users,
        "total_documents": total_docs,
        "documents_by_status": doc_counts,
        "total_ocr_pages": total_ocr_pages,
        "average_confidence": round(avg_confidence, 2),
        "total_corrections": total_corrections,
    }


@router.get("/accuracy")
async def get_accuracy_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get OCR accuracy tracking statistics."""
    return await FeedbackService.get_accuracy_stats(db)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all users."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update user role or status (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)

    await db.flush()
    await db.refresh(user)
    return user


@router.get("/feedback-dataset")
async def export_feedback_dataset(
    format: str = Query("json", pattern="^(json|csv)$"),
    limit: int = Query(1000, ge=1, le=50000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Export OCR→corrected text pairs for model training."""
    if format == "csv":
        csv_data = await FeedbackService.export_dataset_csv(db, limit=limit)
        return PlainTextResponse(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=feedback_dataset.csv"},
        )
    else:
        json_data = await FeedbackService.export_dataset_json(db, limit=limit)
        return PlainTextResponse(
            content=json_data,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=feedback_dataset.json"},
        )
