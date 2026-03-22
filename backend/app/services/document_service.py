"""Document management service."""

import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from fastapi import HTTPException, status, UploadFile
from app.models.document import Document
from app.models.keyword import Keyword
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.utils.storage import save_upload_file, delete_file

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif"}


class DocumentService:
    """Service for document CRUD operations."""

    @staticmethod
    async def upload_document(
        db: AsyncSession,
        file: UploadFile,
        metadata: DocumentCreate,
        user_id: uuid.UUID,
    ) -> Document:
        """Upload a document file with metadata."""
        # Validate file type
        import os

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Save file
        file_info = await save_upload_file(file, subdirectory="documents")

        # Determine pages (1 for images, extract for PDFs)
        total_pages = 1
        if ext == ".pdf":
            try:
                from pdf2image import pdfinfo_from_path

                info = pdfinfo_from_path(file_info["file_path"])
                total_pages = info.get("Pages", 1)
            except Exception:
                total_pages = 1

        # Create document record
        document = Document(
            title=metadata.title,
            department=metadata.department,
            document_date=metadata.document_date,
            document_type=metadata.document_type,
            file_path=file_info["file_path"],
            file_type=ext.lstrip("."),
            file_size=file_info["file_size"],
            total_pages=total_pages,
            status="uploaded",
            uploaded_by=user_id,
        )

        db.add(document)
        await db.flush()
        await db.refresh(document)
        return document

    @staticmethod
    async def list_documents(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        department: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> dict:
        """List documents with pagination and filters."""
        query = select(Document).order_by(desc(Document.created_at))

        if status_filter:
            query = query.where(Document.status == status_filter)
        if department:
            query = query.where(Document.department == department)
        if document_type:
            query = query.where(Document.document_type == document_type)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        documents = result.scalars().all()

        return {
            "documents": documents,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_document(db: AsyncSession, document_id: uuid.UUID) -> Document:
        """Get a single document by ID."""
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return document

    @staticmethod
    async def update_document(
        db: AsyncSession, document_id: uuid.UUID, update_data: DocumentUpdate
    ) -> Document:
        """Update document metadata."""
        document = await DocumentService.get_document(db, document_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(document, key, value)

        await db.flush()
        await db.refresh(document)
        return document

    @staticmethod
    async def delete_document(db: AsyncSession, document_id: uuid.UUID) -> bool:
        """Delete a document and its file."""
        document = await DocumentService.get_document(db, document_id)

        # Delete the file
        await delete_file(document.file_path)

        # Delete from database
        await db.delete(document)
        await db.flush()
        return True

    @staticmethod
    async def add_keywords(
        db: AsyncSession,
        document_id: uuid.UUID,
        keywords: List[str],
        source: str = "manual",
    ) -> List[Keyword]:
        """Add keywords/tags to a document."""
        keyword_objects = []
        for kw in keywords:
            keyword = Keyword(
                document_id=document_id,
                keyword=kw.strip(),
                source=source,
            )
            db.add(keyword)
            keyword_objects.append(keyword)

        await db.flush()
        return keyword_objects
