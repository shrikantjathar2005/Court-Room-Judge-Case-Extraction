"""Document management API routes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import get_db
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentListResponse,
    DocumentUpdate,
)
from app.services.document_service import DocumentService
from app.middleware.auth_middleware import get_current_user, require_admin
from app.models.user import User
from app.utils.storage import get_file_path

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    department: Optional[str] = Form(None),
    document_date: Optional[date] = Form(None),
    document_type: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document with metadata."""
    metadata = DocumentCreate(
        title=title,
        department=department,
        document_date=document_date,
        document_type=document_type,
    )
    document = await DocumentService.upload_document(
        db, file, metadata, current_user.id
    )
    return document


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents with pagination and filters."""
    result = await DocumentService.list_documents(
        db,
        page=page,
        page_size=page_size,
        status_filter=status,
        department=department,
        document_type=document_type,
    )
    return result


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single document by ID."""
    return await DocumentService.get_document(db, document_id)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    update_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update document metadata."""
    return await DocumentService.update_document(db, document_id, update_data)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a document (admin only)."""
    await DocumentService.delete_document(db, document_id)
    return None


@router.get("/{document_id}/file")
async def serve_document_file(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Serve the original document file."""
    document = await DocumentService.get_document(db, document_id)
    file_path = get_file_path(document.file_path)

    if not file_path:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if file_path.startswith("http"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=file_path)

    return FileResponse(
        path=file_path,
        media_type=f"image/{document.file_type}" if document.file_type != "pdf" else "application/pdf",
        filename=f"{document.title}.{document.file_type}",
    )
