"""Search schemas for request/response validation."""

import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    department: Optional[str] = None
    document_type: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    fuzzy: bool = True
    page: int = 1
    page_size: int = 20


class SearchHighlight(BaseModel):
    field: str
    fragments: List[str]


class SearchResultItem(BaseModel):
    document_id: str
    title: str
    department: Optional[str] = None
    document_type: Optional[str] = None
    document_date: Optional[str] = None
    text_snippet: Optional[str] = None
    confidence_score: Optional[float] = None
    score: float
    highlights: List[SearchHighlight] = []


class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    total: int
    page: int
    page_size: int
    query: str


class SuggestResponse(BaseModel):
    suggestions: List[str]
