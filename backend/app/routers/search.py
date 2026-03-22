"""Search API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.search import SearchRequest, SearchResponse, SuggestResponse
from app.services.search_service import SearchService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("/", response_model=SearchResponse)
async def search_documents(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    """Full-text search across all documents."""
    return await SearchService.search(
        query=search_request.query,
        department=search_request.department,
        document_type=search_request.document_type,
        date_from=search_request.date_from,
        date_to=search_request.date_to,
        fuzzy=search_request.fuzzy,
        page=search_request.page,
        page_size=search_request.page_size,
    )


@router.get("/suggest", response_model=SuggestResponse)
async def search_suggestions(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    """Get search autocomplete suggestions."""
    suggestions = await SearchService.suggest(q)
    return SuggestResponse(suggestions=suggestions)
