"""
Document data models for internal use.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""
    chunk_id: str
    document_id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    page_number: Optional[int] = None
    timestamp: Optional[str] = None


@dataclass
class ProcessedDocument:
    """Represents a fully processed document."""
    document_id: str
    filename: str
    file_path: str
    document_type: str
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any] = field(default_factory=dict)
    upload_date: datetime = field(default_factory=datetime.now)
    processed_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "document_type": self.document_type,
            "num_chunks": len(self.chunks),
            "metadata": self.metadata,
            "upload_date": self.upload_date.isoformat(),
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
        }


@dataclass
class ImageDocument:
    """Represents an image document with OCR and embeddings."""
    document_id: str
    filename: str
    file_path: str
    ocr_text: str
    image_embedding: Optional[List[float]] = None
    text_embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "ocr_text": self.ocr_text,
            "metadata": self.metadata,
        }


@dataclass
class AudioDocument:
    """Represents an audio document with transcript."""
    document_id: str
    filename: str
    file_path: str
    transcript: str
    segments: List[Dict[str, Any]] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "transcript": self.transcript,
            "num_segments": len(self.segments),
            "metadata": self.metadata,
        }
