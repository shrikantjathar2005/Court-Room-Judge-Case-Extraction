"""Document schemas for request/response validation."""

import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


class DocumentBase(BaseModel):
    title: str
    department: Optional[str] = None
    document_date: Optional[date] = None
    document_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: uuid.UUID
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    total_pages: int
    status: str
    uploaded_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    document_date: Optional[date] = None
    document_type: Optional[str] = None
    status: Optional[str] = None
