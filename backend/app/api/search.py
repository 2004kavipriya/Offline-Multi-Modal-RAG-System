"""
Search API endpoints.
Handles semantic search across all document types using FAISS.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import numpy as np

from app.models.schemas import SearchQuery, SearchResponse, SearchResult, DocumentType
from app.models.database import DocumentChunk, ImageEmbedding, Document
from app.models.db_session import get_db
from app.config import get_settings
from app.embeddings.text_embedder import TextEmbedder
from app.embeddings.image_embedder import ImageEmbedder
from app.vectorstore.faiss_store import get_text_store, get_image_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])

# Initialize components
settings = get_settings()
text_embedder = TextEmbedder(model_name=settings.text_embedding_model)
image_embedder = ImageEmbedder(model_name=settings.image_embedding_model)


@router.post("/", response_model=SearchResponse)
async def search(query: SearchQuery, db: Session = Depends(get_db)):
    """
    Perform semantic search across all documents.
    
    Args:
        query: Search query
        db: Database session
        
    Returns:
        Search results
    """
    try:
        # Generate query embedding
        query_embedding = text_embedder.embed(query.query)[0]
        
        # Search in FAISS
        text_store = get_text_store(dimension=text_embedder.get_embedding_dimension())
        faiss_results = text_store.search(query_embedding, top_k=query.top_k or settings.top_k_results)
        
        if not faiss_results:
            return SearchResponse(
                success=True,
                query=query.query,
                results=[],
                total_results=0
            )
        
        # Get chunk IDs and scores
        chunk_ids = [chunk_id for chunk_id, _ in faiss_results]
        scores = {chunk_id: score for chunk_id, score in faiss_results}
        
        # Fetch chunks from database
        chunks = db.query(DocumentChunk).filter(DocumentChunk.id.in_(chunk_ids)).all()
        
        # Get document info
        document_ids = list(set(chunk.document_id for chunk in chunks))
        documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
        doc_map = {doc.id: doc for doc in documents}
        
        # Filter by document type if specified
        if query.document_types:
            allowed_types = [dt.value for dt in query.document_types]
            chunks = [chunk for chunk in chunks if doc_map.get(chunk.document_id) and doc_map[chunk.document_id].document_type in allowed_types]
        
        # Format results
        search_results = []
        for chunk in chunks:
            doc = doc_map.get(chunk.document_id)
            if not doc:
                continue
            
            search_results.append(SearchResult(
                document_id=chunk.document_id,
                filename=doc.filename,
                document_type=DocumentType(doc.document_type),
                content=chunk.content,
                relevance_score=scores.get(chunk.id, 0.0),
                metadata=chunk.chunk_metadata or {},
                page_number=chunk.page_number,
                timestamp=chunk.timestamp
            ))
        
        # Sort by relevance
        search_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"Search for '{query.query}' returned {len(search_results)} results")
        
        return SearchResponse(
            success=True,
            query=query.query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cross-modal", response_model=SearchResponse)
async def cross_modal_search(query: SearchQuery, db: Session = Depends(get_db)):
    """
    Perform cross-modal search (text query for images and text).
    
    Args:
        query: Search query
        db: Database session
        
    Returns:
        Search results including images
    """
    try:
        # Generate CLIP text embedding for image search
        clip_embedding = image_embedder.embed_text(query.query)
        
        # Search in image FAISS store
        image_store = get_image_store(dimension=clip_embedding.shape[0])
        image_results = image_store.search(clip_embedding, top_k=query.top_k or settings.top_k_results)
        
        # Generate text embedding for text search
        text_embedding = text_embedder.embed(query.query)[0]
        text_store = get_text_store(dimension=text_embedder.get_embedding_dimension())
        text_results = text_store.search(text_embedding, top_k=query.top_k or settings.top_k_results)
        
        all_results = []
        
        # Process image results
        if image_results:
            image_ids = [img_id for img_id, _ in image_results]
            image_scores = {img_id: score for img_id, score in image_results}
            
            images = db.query(ImageEmbedding).filter(ImageEmbedding.id.in_(image_ids)).all()
            image_doc_ids = [img.document_id for img in images]
            image_docs = db.query(Document).filter(Document.id.in_(image_doc_ids)).all()
            image_doc_map = {doc.id: doc for doc in image_docs}
            
            for img in images:
                doc = image_doc_map.get(img.document_id)
                if not doc:
                    continue
                
                all_results.append(SearchResult(
                    document_id=img.document_id,
                    filename=doc.filename,
                    document_type=DocumentType.IMAGE,
                    content=img.ocr_text or f"Image: {doc.filename}",
                    relevance_score=image_scores.get(img.id, 0.0),
                    metadata=img.image_metadata or {}
                ))
        
        # Process text results
        if text_results:
            chunk_ids = [chunk_id for chunk_id, _ in text_results]
            chunk_scores = {chunk_id: score for chunk_id, score in text_results}
            
            chunks = db.query(DocumentChunk).filter(DocumentChunk.id.in_(chunk_ids)).all()
            chunk_doc_ids = [chunk.document_id for chunk in chunks]
            chunk_docs = db.query(Document).filter(Document.id.in_(chunk_doc_ids)).all()
            chunk_doc_map = {doc.id: doc for doc in chunk_docs}
            
            for chunk in chunks:
                doc = chunk_doc_map.get(chunk.document_id)
                if not doc:
                    continue
                
                all_results.append(SearchResult(
                    document_id=chunk.document_id,
                    filename=doc.filename,
                    document_type=DocumentType(doc.document_type),
                    content=chunk.content,
                    relevance_score=chunk_scores.get(chunk.id, 0.0),
                    metadata=chunk.chunk_metadata or {},
                    page_number=chunk.page_number,
                    timestamp=chunk.timestamp
                ))
        
        # Sort by relevance
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        all_results = all_results[:query.top_k or settings.top_k_results]
        
        logger.info(f"Cross-modal search for '{query.query}' returned {len(all_results)} results")
        
        return SearchResponse(
            success=True,
            query=query.query,
            results=all_results,
            total_results=len(all_results)
        )
        
    except Exception as e:
        logger.error(f"Error performing cross-modal search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
