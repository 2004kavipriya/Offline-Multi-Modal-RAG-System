"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings, ensure_directories
from app.models.db_session import init_db
from app.api import upload, search, query
from app.models.schemas import HealthResponse
from app import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Ensure directories exist
ensure_directories()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Multimodal RAG system with FAISS + PostgreSQL + MinIO"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(search.router)
app.include_router(query.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": __version__,
        "status": "running",
        "message": "Multimodal RAG API is running",
        "architecture": "FAISS + PostgreSQL + MinIO"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    """Health check endpoint."""
    from app.embeddings.text_embedder import TextEmbedder
    from app.embeddings.image_embedder import ImageEmbedder
    from app.processors.audio_processor import AudioProcessor
    from app.llm.generator import LLMGenerator
    from app.vectorstore.minio_storage import get_minio_client
    
    # Check if models are loaded
    models_loaded = {
        "text_embedder": False,
        "image_embedder": False,
        "audio_processor": False,
        "llm": False,
        "minio": False
    }
    
    try:
        text_embedder = TextEmbedder(model_name=settings.text_embedding_model)
        text_embedder.load_model()
        models_loaded["text_embedder"] = True
    except:
        pass
    
    try:
        image_embedder = ImageEmbedder(model_name=settings.image_embedding_model)
        image_embedder.load_model()
        models_loaded["image_embedder"] = True
    except:
        pass
    
    try:
        audio_processor = AudioProcessor(model_name=settings.whisper_model)
        audio_processor.load_model()
        models_loaded["audio_processor"] = True
    except:
        pass
    
    try:
        llm = LLMGenerator(model_name=settings.llm_model)
        models_loaded["llm"] = llm.check_model_available()
    except:
        pass
    
    try:
        minio = get_minio_client()
        models_loaded["minio"] = True
    except:
        pass
    
    return HealthResponse(
        status="healthy" if all(models_loaded.values()) else "degraded",
        version=__version__,
        models_loaded=models_loaded
    )


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting {settings.app_name} v{__version__}")
    logger.info("Architecture: FAISS + PostgreSQL + MinIO")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
    
    # Initialize MinIO
    try:
        from app.vectorstore.minio_storage import get_minio_client
        get_minio_client()
        logger.info("MinIO client initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing MinIO: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
