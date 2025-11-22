"""
Configuration module for the Multimodal RAG system.
Loads settings from environment variables and provides centralized config access.
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    app_name: str = "MultimodalRAG"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Paths
    faiss_index_dir: str = "./data/faiss_indexes"
    models_dir: str = "./models"
    
    # PostgreSQL Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/multimodal_rag"
    db_echo: bool = False
    
    # MinIO Object Storage
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "multimodal-rag"
    minio_secure: bool = False
    
    # Model Settings
    text_embedding_model: str = "all-MiniLM-L6-v2"
    image_embedding_model: str = "openai/clip-vit-base-patch32"
    whisper_model: str = "base"
    llm_model: str = "llama2:latest"
    
    # Chunking Settings
    chunk_size: int = 800
    chunk_overlap: int = 100
    
    # Search Settings
    top_k_results: int = 10
    similarity_threshold: float = 0.7
    
    # LLM Settings
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        settings.faiss_index_dir,
        settings.models_dir,
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
