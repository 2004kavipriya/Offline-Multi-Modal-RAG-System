"""
Pydantic schemas for request/response models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"


class UploadResponse(BaseModel):
    """Response model for file upload."""
    success: bool
    message: str
    document_id: str
    filename: str
    document_type: DocumentType
    processed: bool = False


class SearchQuery(BaseModel):
    """Request model for search queries."""
    query: str = Field(..., description="Search query text")
    document_types: Optional[List[DocumentType]] = Field(
        default=None, 
        description="Filter by document types"
    )
    top_k: Optional[int] = Field(default=5, description="Number of results to return")


class Citation(BaseModel):
    """Citation information for a source."""
    citation_id: int
    document_id: str
    filename: str
    document_type: DocumentType
    page_number: Optional[int] = None
    timestamp: Optional[str] = None
    excerpt: str
    relevance_score: float


class SearchResult(BaseModel):
    """Individual search result."""
    document_id: str
    filename: str
    document_type: DocumentType
    content: str
    relevance_score: float
    metadata: Dict[str, Any] = {}
    page_number: Optional[int] = None
    timestamp: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for search results."""
    success: bool
    query: str
    results: List[SearchResult]
    total_results: int


class RAGQuery(BaseModel):
    """Request model for RAG queries."""
    query: str = Field(..., description="Natural language question")
    document_types: Optional[List[DocumentType]] = Field(
        default=None,
        description="Filter by document types"
    )
    top_k: Optional[int] = Field(default=5, description="Number of context documents")


class RAGResponse(BaseModel):
    """Response model for RAG queries."""
    success: bool
    query: str
    answer: str
    citations: List[Citation]
    context_used: int


class DocumentMetadata(BaseModel):
    """Metadata for a processed document."""
    document_id: str
    filename: str
    document_type: DocumentType
    upload_date: datetime
    file_size: int
    num_chunks: int
    processed: bool
    metadata: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    models_loaded: Dict[str, bool]
