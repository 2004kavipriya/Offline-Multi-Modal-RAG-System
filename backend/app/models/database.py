"""
PostgreSQL database models using SQLAlchemy.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Document(Base):
    """Document metadata table."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    document_type = Column(String, nullable=False)  # pdf, docx, image, audio
    file_size = Column(Integer)
    minio_path = Column(String, nullable=False)  # Path in MinIO
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_date = Column(DateTime, nullable=True)
    doc_metadata = Column(JSON, default={})
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "document_type": self.document_type,
            "file_size": self.file_size,
            "minio_path": self.minio_path,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "processed": self.processed,
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "metadata": self.doc_metadata
        }


class DocumentChunk(Base):
    """Document chunks table."""
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    faiss_index = Column(Integer, nullable=True)  # Index in FAISS vector store
    page_number = Column(Integer, nullable=True)  # For PDFs
    timestamp = Column(String, nullable=True)  # For audio (e.g., "00:12-00:45")
    start_time = Column(Float, nullable=True)  # For audio (seconds)
    end_time = Column(Float, nullable=True)  # For audio (seconds)
    chunk_metadata = Column(JSON, default={})
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "faiss_index": self.faiss_index,
            "page_number": self.page_number,
            "timestamp": self.timestamp,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metadata": self.chunk_metadata,
            "created_date": self.created_date.isoformat() if self.created_date else None
        }


class ImageEmbedding(Base):
    """Image embeddings table (separate from text chunks)."""
    __tablename__ = "image_embeddings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    faiss_index = Column(Integer, nullable=True)  # Index in image FAISS store
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    image_metadata = Column(JSON, default={})
    created_date = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "faiss_index": self.faiss_index,
            "ocr_text": self.ocr_text,
            "ocr_confidence": self.ocr_confidence,
            "image_metadata": self.image_metadata,
            "created_date": self.created_date.isoformat() if self.created_date else None
        }
