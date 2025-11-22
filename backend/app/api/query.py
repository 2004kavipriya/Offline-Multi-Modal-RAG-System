"""
RAG query API endpoints.
Handles natural language queries with LLM-generated responses.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.models.schemas import RAGQuery, RAGResponse, Citation, DocumentType
from app.models.database import DocumentChunk, Document
from app.models.db_session import get_db
from app.config import get_settings
from app.embeddings.text_embedder import TextEmbedder
from app.vectorstore.faiss_store import get_text_store
from app.llm.generator import LLMGenerator
from app.utils.citations import CitationManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/query", tags=["query"])

# Initialize components
settings = get_settings()
text_embedder = TextEmbedder(model_name=settings.text_embedding_model)
llm_generator = LLMGenerator(
    model_name=settings.llm_model,
    temperature=settings.llm_temperature,
    max_tokens=settings.llm_max_tokens
)


@router.post("/", response_model=RAGResponse)
async def query(query: RAGQuery, db: Session = Depends(get_db)):
    """
    Process a natural language query with RAG.
    
    Args:
        query: RAG query
        db: Database session
        
    Returns:
        Generated answer with citations
    """
    try:
        # Generate query embedding
        query_embedding = text_embedder.embed(query.query)[0]
        
        # Search in FAISS
        text_store = get_text_store(dimension=text_embedder.get_embedding_dimension())
        faiss_results = text_store.search(query_embedding, top_k=query.top_k or settings.top_k_results)
        
        if not faiss_results:
            return RAGResponse(
                success=True,
                query=query.query,
                answer="I couldn't find any relevant information to answer your question.",
                citations=[],
                context_used=0
            )
        
        # Get chunks from database
        chunk_ids = [chunk_id for chunk_id, _ in faiss_results]
        scores = {chunk_id: score for chunk_id, score in faiss_results}
        
        chunks = db.query(DocumentChunk).filter(DocumentChunk.id.in_(chunk_ids)).all()
        
        # Get documents
        document_ids = list(set(chunk.document_id for chunk in chunks))
        documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
        doc_map = {doc.id: doc for doc in documents}
        
        # Filter by document type if specified
        if query.document_types:
            allowed_types = [dt.value for dt in query.document_types]
            chunks = [chunk for chunk in chunks if doc_map.get(chunk.document_id) and doc_map[chunk.document_id].document_type in allowed_types]
        
        if not chunks:
            return RAGResponse(
                success=True,
                query=query.query,
                answer="I couldn't find any relevant information in the specified document types.",
                citations=[],
                context_used=0
            )
        
        # Prepare context for LLM
        context_documents = []
        for chunk in chunks:
            doc = doc_map.get(chunk.document_id)
            if not doc:
                continue
            
            context_documents.append({
                'document': chunk.content,
                'metadata': {
                    'filename': doc.filename,
                    'document_type': doc.document_type,
                    'page_number': chunk.page_number,
                    'timestamp': chunk.timestamp,
                    **(chunk.chunk_metadata or {})
                },
                'relevance_score': scores.get(chunk.id, 0.0)
            })
        
        # Generate answer using LLM
        answer = llm_generator.generate_rag_response(
            query=query.query,
            context_documents=context_documents
        )
        
        # Create citations
        citation_manager = CitationManager()
        citations = []
        
        for i, chunk in enumerate(chunks):
            doc = doc_map.get(chunk.document_id)
            if not doc:
                continue
            
            citation_id = citation_manager.add_citation(
                document_id=chunk.document_id,
                filename=doc.filename,
                document_type=doc.document_type,
                excerpt=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                relevance_score=scores.get(chunk.id, 0.0),
                page_number=chunk.page_number,
                timestamp=chunk.timestamp,
                metadata=chunk.chunk_metadata or {}
            )
            
            citations.append(Citation(
                citation_id=citation_id,
                document_id=chunk.document_id,
                filename=doc.filename,
                document_type=DocumentType(doc.document_type),
                page_number=chunk.page_number,
                timestamp=chunk.timestamp,
                excerpt=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                relevance_score=scores.get(chunk.id, 0.0)
            ))
        
        logger.info(f"Query '{query.query}' processed with {len(citations)} citations")
        
        return RAGResponse(
            success=True,
            query=query.query,
            answer=answer,
            citations=citations,
            context_used=len(context_documents)
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Check if LLM is available.
    
    Returns:
        Health status
    """
    try:
        llm_available = llm_generator.check_model_available()
        
        return {
            "status": "healthy" if llm_available else "degraded",
            "llm_available": llm_available,
            "model": settings.llm_model
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "llm_available": False,
            "error": str(e)
        }
