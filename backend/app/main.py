"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.database import init_db
from app.routers import auth, documents, ocr, corrections, search, admin
from app.services.search_service import SearchService, close_es_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    logger.info("Starting DocDigitizer API...")
    await init_db()
    logger.info("Database initialized")

    # Create uploads directory
    uploads_dir = Path(settings.UPLOAD_DIR)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Elasticsearch index
    try:
        await SearchService.create_index()
        logger.info("Elasticsearch index ready")
    except Exception as e:
        logger.warning(f"Elasticsearch not available: {e}")

    yield

    # Shutdown
    logger.info("Shutting down DocDigitizer API...")
    await close_es_client()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="API for digitizing, processing, and searching old government documents in Devanagari (Hindi/Marathi)",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
uploads_path = Path(settings.UPLOAD_DIR)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Register routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(ocr.router)
app.include_router(corrections.router)
app.include_router(search.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
