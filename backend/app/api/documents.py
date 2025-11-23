"""
Documents API endpoints.
Handles listing and managing uploaded documents.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import logging
import io

from app.models.schemas import DocumentMetadata
from app.models.database import Document
from app.models.db_session import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/", response_model=List[DocumentMetadata])
async def list_documents(db: Session = Depends(get_db)):
    """
    Get a list of all uploaded documents.
    
    Args:
        db: Database session
        
    Returns:
        List of document metadata
    """
    try:
        documents = db.query(Document).order_by(Document.upload_date.desc()).all()
        
        result = []
        for doc in documents:
            # Count chunks for this document
            num_chunks = len(doc.chunks) if doc.chunks else 0
            
            result.append(DocumentMetadata(
                document_id=doc.id,
                filename=doc.filename,
                document_type=doc.document_type,
                upload_date=doc.upload_date,
                file_size=doc.file_size,
                num_chunks=num_chunks,
                processed=doc.processed,
                metadata=doc.doc_metadata or {}
            ))
        
        logger.info(f"Retrieved {len(result)} documents")
        return result
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Document metadata
    """
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        num_chunks = len(doc.chunks) if doc.chunks else 0
        
        return DocumentMetadata(
            document_id=doc.id,
            filename=doc.filename,
            document_type=doc.document_type,
            upload_date=doc.upload_date,
            file_size=doc.file_size,
            num_chunks=num_chunks,
            processed=doc.processed,
            metadata=doc.doc_metadata or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    Delete a document and all its associated data.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from database (cascades to chunks and embeddings)
        db.delete(doc)
        db.commit()
        
        logger.info(f"Deleted document: {doc.filename} ({document_id})")
        
        return {
            "success": True,
            "message": f"Document '{doc.filename}' deleted successfully",
            "document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/download")
async def download_document(document_id: str, db: Session = Depends(get_db)):
    """
    Download the original document file from MinIO.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        File stream
    """
    try:
        from app.vectorstore.minio_storage import get_minio_client
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get MinIO client
        minio_client = get_minio_client()
        
        # Download file from MinIO as bytes
        file_data = minio_client.download_bytes(doc.minio_path)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        # Determine content type
        content_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image': 'image/jpeg',
            'audio': 'audio/mpeg',
            'text': 'text/plain'
        }
        content_type = content_types.get(doc.document_type, 'application/octet-stream')
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{doc.filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
