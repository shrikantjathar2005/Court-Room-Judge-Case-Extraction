"""Search service using Elasticsearch."""

import logging
from typing import Optional
from datetime import date
from elasticsearch import AsyncElasticsearch
from app.config import settings

logger = logging.getLogger(__name__)

# Elasticsearch client (initialized lazily)
_es_client: Optional[AsyncElasticsearch] = None


async def get_es_client() -> AsyncElasticsearch:
    """Get or create Elasticsearch client."""
    global _es_client
    if _es_client is None:
        _es_client = AsyncElasticsearch(
            [settings.ELASTICSEARCH_URL],
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True,
        )
    return _es_client


async def close_es_client():
    """Close Elasticsearch client."""
    global _es_client
    if _es_client:
        await _es_client.close()
        _es_client = None


class SearchService:
    """Service for Elasticsearch-based document search."""

    INDEX_NAME = settings.ELASTICSEARCH_INDEX

    @staticmethod
    async def create_index():
        """Create Elasticsearch index with proper mapping for Devanagari text."""
        es = await get_es_client()

        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "devanagari_analyzer": {
                            "type": "custom",
                            "tokenizer": "icu_tokenizer",
                            "filter": ["lowercase", "icu_folding"],
                        },
                        "text_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase"],
                        },
                    }
                },
            },
            "mappings": {
                "properties": {
                    "document_id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "text_analyzer",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "department": {"type": "keyword"},
                    "document_type": {"type": "keyword"},
                    "document_date": {"type": "date"},
                    "page_number": {"type": "integer"},
                    "text": {
                        "type": "text",
                        "analyzer": "text_analyzer",
                    },
                    "confidence_score": {"type": "float"},
                    "keywords": {"type": "keyword"},
                }
            },
        }

        try:
            exists = await es.indices.exists(index=SearchService.INDEX_NAME)
            if not exists:
                await es.indices.create(
                    index=SearchService.INDEX_NAME, body=index_settings
                )
                logger.info(f"Created Elasticsearch index: {SearchService.INDEX_NAME}")
        except Exception as e:
            logger.warning(f"Failed to create ES index: {e}")

    @staticmethod
    async def index_document(
        document_id: str,
        title: str,
        department: str,
        document_type: str,
        document_date: Optional[str],
        page_number: int,
        text: str,
        confidence_score: float,
        keywords: list = None,
    ):
        """Index a document page in Elasticsearch."""
        es = await get_es_client()

        doc = {
            "document_id": document_id,
            "title": title,
            "department": department or "",
            "document_type": document_type or "",
            "document_date": document_date,
            "page_number": page_number,
            "text": text,
            "confidence_score": confidence_score,
            "keywords": keywords or [],
        }

        doc_id = f"{document_id}_{page_number}"

        try:
            await es.index(index=SearchService.INDEX_NAME, id=doc_id, body=doc)
            logger.info(f"Indexed document {document_id} page {page_number}")
        except Exception as e:
            logger.error(f"Failed to index document: {e}")

    @staticmethod
    async def search(
        query: str,
        department: Optional[str] = None,
        document_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        fuzzy: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Full-text search with filters and fuzzy matching."""
        es = await get_es_client()

        # Build query
        must_clauses = []
        filter_clauses = []

        # Main text query
        if fuzzy:
            must_clauses.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["text^2", "title^3", "keywords^2"],
                        "fuzziness": "AUTO",
                        "prefix_length": 1,
                    }
                }
            )
        else:
            must_clauses.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["text^2", "title^3", "keywords^2"],
                    }
                }
            )

        # Filters
        if department:
            filter_clauses.append({"term": {"department": department}})
        if document_type:
            filter_clauses.append({"term": {"document_type": document_type}})
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from.isoformat()
            if date_to:
                date_range["lte"] = date_to.isoformat()
            filter_clauses.append({"range": {"document_date": date_range}})

        search_body = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses,
                }
            },
            "highlight": {
                "fields": {
                    "text": {
                        "fragment_size": 200,
                        "number_of_fragments": 3,
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"],
                    },
                    "title": {
                        "fragment_size": 100,
                        "number_of_fragments": 1,
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"],
                    },
                }
            },
            "from": (page - 1) * page_size,
            "size": page_size,
            "sort": [{"_score": "desc"}, {"document_date": "desc"}],
        }

        try:
            response = await es.search(index=SearchService.INDEX_NAME, body=search_body)

            hits = response["hits"]
            results = []

            for hit in hits["hits"]:
                source = hit["_source"]
                highlights = []

                if "highlight" in hit:
                    for field, fragments in hit["highlight"].items():
                        highlights.append(
                            {"field": field, "fragments": fragments}
                        )

                results.append(
                    {
                        "document_id": source["document_id"],
                        "title": source["title"],
                        "department": source.get("department"),
                        "document_type": source.get("document_type"),
                        "document_date": source.get("document_date"),
                        "text_snippet": source.get("text", "")[:300],
                        "confidence_score": source.get("confidence_score"),
                        "score": hit["_score"],
                        "highlights": highlights,
                    }
                )

            return {
                "results": results,
                "total": hits["total"]["value"],
                "page": page,
                "page_size": page_size,
                "query": query,
            }

        except Exception as e:
            logger.warning(f"Elasticsearch search failed, falling back to database: {e}")
            from app.database import async_session
            from sqlalchemy import select, or_, func
            from app.models.document import Document
            
            async with async_session() as db:
                stmt = select(Document).where(
                    or_(
                        Document.title.like(f"%{query}%"),
                        Document.department.like(f"%{query}%")
                    )
                )
                
                if department:
                    stmt = stmt.where(Document.department == department)
                if document_type:
                    stmt = stmt.where(Document.document_type == document_type)
                    
                result = await db.execute(stmt)
                docs = result.scalars().all()
                
                results = []
                for doc in docs:
                    results.append({
                        "document_id": str(doc.id),
                        "title": doc.title,
                        "department": doc.department,
                        "document_type": doc.document_type,
                        "document_date": doc.document_date.isoformat() if doc.document_date else None,
                        "text_snippet": "Full text not available in fallback search. Click to view.",
                        "confidence_score": 0.0,
                        "score": 1.0,
                        "highlights": []
                    })
                
                return {
                    "results": results,
                    "total": len(results),
                    "page": 1,
                    "page_size": len(results) or 20,
                    "query": query,
                }

    @staticmethod
    async def suggest(query: str, size: int = 5) -> list:
        """Get search suggestions/autocomplete."""
        es = await get_es_client()

        try:
            response = await es.search(
                index=SearchService.INDEX_NAME,
                body={
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title", "keywords"],
                            "type": "phrase_prefix",
                        }
                    },
                    "size": size,
                    "_source": ["title"],
                },
            )

            suggestions = []
            for hit in response["hits"]["hits"]:
                title = hit["_source"].get("title", "")
                if title and title not in suggestions:
                    suggestions.append(title)

            return suggestions

        except Exception as e:
            logger.error(f"Suggest failed: {e}")
            return []

    @staticmethod
    async def delete_document(document_id: str):
        """Remove all pages of a document from the index."""
        es = await get_es_client()

        try:
            await es.delete_by_query(
                index=SearchService.INDEX_NAME,
                body={"query": {"term": {"document_id": document_id}}},
            )
        except Exception as e:
            logger.error(f"Failed to delete from ES: {e}")
