"""Correction schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class CorrectionCreate(BaseModel):
    corrected_text: str


class CorrectionResponse(BaseModel):
    id: uuid.UUID
    ocr_result_id: uuid.UUID
    original_text: Optional[str] = None
    corrected_text: Optional[str] = None
    corrected_by: Optional[uuid.UUID] = None
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


class CorrectionHistoryResponse(BaseModel):
    ocr_result_id: uuid.UUID
    corrections: List[CorrectionResponse]
    total_versions: int
