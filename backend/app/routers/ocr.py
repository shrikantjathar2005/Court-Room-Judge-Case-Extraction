"""OCR processing API routes."""

from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, async_session
from app.schemas.ocr import OCRProcessRequest, OCRStatusResponse, OCRResultResponse
from app.services.ocr_service import OCRService
from app.services.search_service import SearchService
from app.services.document_service import DocumentService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from typing import List

router = APIRouter(prefix="/api/ocr", tags=["OCR Processing"])


async def _background_ocr_task(document_id: UUID, languages: str, preprocess: bool):
    """Background task for OCR processing."""
    async with async_session() as db:
        try:
            ocr_results = await OCRService.process_document(
                db, document_id, languages=languages, preprocess=preprocess
            )
            await db.commit()

            # Index results in Elasticsearch
            document = await DocumentService.get_document(db, document_id)
            for result in ocr_results:
                if result.status == "completed" and result.raw_text:
                    try:
                        await SearchService.index_document(
                            document_id=str(document_id),
                            title=document.title,
                            department=document.department,
                            document_type=document.document_type,
                            document_date=str(document.document_date) if document.document_date else None,
                            page_number=result.page_number,
                            text=result.raw_text,
                            confidence_score=result.confidence_score or 0,
                        )
                    except Exception as es_err:
                        import logging
                        logging.getLogger(__name__).warning(f"Failed to index in Elasticsearch (OCR completed successfully though): {es_err}")
        except Exception as e:
            await db.rollback()
            import logging
            from sqlalchemy import update
            from app.models.document import Document
            logging.getLogger(__name__).error(f"Background OCR failed: {e}")
            try:
                await db.execute(update(Document).where(Document.id == document_id).values(status="failed"))
                await db.commit()
            except Exception as inner_e:
                logging.getLogger(__name__).error(f"Failed to update document status to failed: {inner_e}")


@router.post("/process/{document_id}", status_code=202)
async def trigger_ocr_processing(
    document_id: UUID,
    request: OCRProcessRequest = OCRProcessRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger asynchronous OCR processing for a document."""
    # Verify document exists
    document = await DocumentService.get_document(db, document_id)

    if document.status == "processing":
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already being processed",
        )

    # Update status to processing
    document.status = "processing"
    await db.flush()

    # Start background OCR task
    background_tasks.add_task(
        _background_ocr_task,
        document_id,
        request.languages,
        request.preprocess,
    )

    return {
        "message": "OCR processing started",
        "document_id": str(document_id),
        "status": "processing",
    }


@router.get("/status/{document_id}", response_model=OCRStatusResponse)
async def get_ocr_status(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check OCR processing status for a document."""
    return await OCRService.get_ocr_status(db, document_id)


@router.get("/results/{document_id}", response_model=List[OCRResultResponse])
async def get_ocr_results(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get OCR results for a document."""
    return await OCRService.get_ocr_results(db, document_id)
