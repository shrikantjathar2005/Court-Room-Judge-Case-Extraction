"""OCR schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class OCRResultResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    page_number: int
    raw_text: Optional[str] = None
    confidence_score: Optional[float] = None
    language: str
    processing_time: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OCRProcessRequest(BaseModel):
    languages: str = "hin+eng"
    preprocess: bool = True


class OCRStatusResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    total_pages: int
    processed_pages: int
    average_confidence: Optional[float] = None
    results: List[OCRResultResponse] = []
