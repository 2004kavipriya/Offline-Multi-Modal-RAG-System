"""
File upload API endpoints.
Handles file uploads and document processing with MinIO storage.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import tempfile
import logging
from typing import List
from datetime import datetime

from app.models.schemas import UploadResponse, DocumentType
from app.models.database import Document, DocumentChunk, ImageEmbedding
from app.models.db_session import get_db
from app.config import get_settings
from app.processors.pdf_processor import PDFProcessor
from app.processors.docx_processor import DOCXProcessor
from app.processors.image_processor import ImageProcessor
from app.processors.audio_processor import AudioProcessor
from app.embeddings.text_embedder import TextEmbedder
from app.embeddings.image_embedder import ImageEmbedder
from app.vectorstore.faiss_store import get_text_store, get_image_store
from app.vectorstore.minio_storage import get_minio_client
from app.utils.chunking import TextChunker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["upload"])

# Initialize components
settings = get_settings()
pdf_processor = PDFProcessor()
docx_processor = DOCXProcessor()
image_processor = ImageProcessor()
audio_processor = AudioProcessor(model_name=settings.whisper_model)
text_embedder = TextEmbedder(model_name=settings.text_embedding_model)
image_embedder = ImageEmbedder(model_name=settings.image_embedding_model)
text_chunker = TextChunker(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)


def get_document_type(filename: str) -> DocumentType:
    """Determine document type from filename."""
    ext = Path(filename).suffix.lower()
    
    if ext == '.pdf':
        return DocumentType.PDF
    elif ext in ['.docx', '.doc']:
        return DocumentType.DOCX
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:
        return DocumentType.IMAGE
    elif ext in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
        return DocumentType.AUDIO
    else:
        return DocumentType.TEXT


@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process a file.
    
    Args:
        file: Uploaded file
        db: Database session
        
    Returns:
        Upload response with document ID
    """
    try:
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Determine document type
        doc_type = get_document_type(file.filename)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Upload to MinIO
        minio_client = get_minio_client()
        minio_path = f"{doc_type.value}/{document_id}/{file.filename}"
        minio_client.upload_file(temp_path, minio_path)
        
        # Create database record
        document = Document(
            id=document_id,
            filename=file.filename,
            original_filename=file.filename,
            document_type=doc_type.value,
            file_size=len(content),
            minio_path=minio_path,
            upload_date=datetime.utcnow(),
            processed=False
        )
        db.add(document)
        db.commit()
        
        logger.info(f"File uploaded: {file.filename} ({doc_type.value})")
        
        # Process file based on type
        success = await process_document(
            document_id=document_id,
            file_path=temp_path,
            filename=file.filename,
            doc_type=doc_type,
            db=db
        )
        
        # Update processed status
        if success:
            document.processed = True
            document.processed_date = datetime.utcnow()
            db.commit()
        
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)
        
        return UploadResponse(
            success=True,
            message=f"File uploaded successfully",
            document_id=document_id,
            filename=file.filename,
            document_type=doc_type,
            processed=success
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_document(
    document_id: str,
    file_path: str,
    filename: str,
    doc_type: DocumentType,
    db: Session
) -> bool:
    """
    Process a document and add to vector store.
    
    Args:
        document_id: Unique document ID
        file_path: Path to the file
        filename: Original filename
        doc_type: Document type
        db: Database session
        
    Returns:
        True if successful
    """
    try:
        if doc_type == DocumentType.PDF:
            return await process_pdf(document_id, file_path, filename, db)
        elif doc_type == DocumentType.DOCX:
            return await process_docx(document_id, file_path, filename, db)
        elif doc_type == DocumentType.IMAGE:
            return await process_image(document_id, file_path, filename, db)
        elif doc_type == DocumentType.AUDIO:
            return await process_audio(document_id, file_path, filename, db)
        else:
            logger.warning(f"Unsupported document type: {doc_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        return False


async def process_pdf(document_id: str, file_path: str, filename: str, db: Session) -> bool:
    """Process PDF document."""
    try:
        # Extract text
        result = pdf_processor.extract_text(file_path)
        
        if not result['success']:
            return False
        
        # Get FAISS store
        text_store = get_text_store(dimension=text_embedder.get_embedding_dimension())
        
        # Process each page
        all_chunks = []
        all_embeddings = []
        chunk_records = []
        
        for page_data in result['pages']:
            page_num = page_data['page_number']
            text = page_data['text']
            
            # Chunk the page text
            page_chunks = text_chunker.chunk_text(
                text,
                metadata={'page_number': page_num}
            )
            
            for chunk in page_chunks:
                all_chunks.append(chunk['text'])
                
                # Create chunk record
                chunk_record = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk['chunk_id'],
                    content=chunk['text'],
                    page_number=page_num,
                    chunk_metadata={'page_number': page_num}
                )
                chunk_records.append(chunk_record)
        
        # Generate embeddings
        embeddings = text_embedder.embed_batch(all_chunks)
        
        # Add to database
        db.add_all(chunk_records)
        db.flush()  # Get IDs
        
        # Add to FAISS
        chunk_ids = [chunk.id for chunk in chunk_records]
        faiss_indices = text_store.add_vectors(embeddings, chunk_ids)
        
        # Update FAISS indices in database
        for chunk, faiss_idx in zip(chunk_records, faiss_indices):
            chunk.faiss_index = faiss_idx
        
        db.commit()
        
        logger.info(f"Processed PDF: {filename} ({len(all_chunks)} chunks)")
        return True
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        db.rollback()
        return False


async def process_docx(document_id: str, file_path: str, filename: str, db: Session) -> bool:
    """Process DOCX document."""
    try:
        # Extract text
        result = docx_processor.extract_text(file_path)
        
        if not result['success']:
            return False
        
        # Get FAISS store
        text_store = get_text_store(dimension=text_embedder.get_embedding_dimension())
        
        # Chunk the text
        chunks_data = text_chunker.chunk_text(result['text'])
        
        chunk_records = []
        for chunk in chunks_data:
            chunk_record = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk['chunk_id'],
                content=chunk['text'],
                chunk_metadata={}
            )
            chunk_records.append(chunk_record)
        
        # Generate embeddings
        chunks = [chunk['text'] for chunk in chunks_data]
        embeddings = text_embedder.embed_batch(chunks)
        
        # Add to database
        db.add_all(chunk_records)
        db.flush()
        
        # Add to FAISS
        chunk_ids = [chunk.id for chunk in chunk_records]
        faiss_indices = text_store.add_vectors(embeddings, chunk_ids)
        
        # Update FAISS indices
        for chunk, faiss_idx in zip(chunk_records, faiss_indices):
            chunk.faiss_index = faiss_idx
        
        db.commit()
        
        logger.info(f"Processed DOCX: {filename} ({len(chunks)} chunks)")
        return True
        
    except Exception as e:
        logger.error(f"Error processing DOCX: {str(e)}")
        db.rollback()
        return False


async def process_image(document_id: str, file_path: str, filename: str, db: Session) -> bool:
    """Process image document."""
    try:
        # Extract text via OCR
        ocr_result = image_processor.extract_text(file_path)
        
        # Generate image embedding
        img_embedding = image_embedder.embed_image(file_path)
        
        # Create image embedding record
        image_record = ImageEmbedding(
            document_id=document_id,
            ocr_text=ocr_result.get('text', ''),
            ocr_confidence=ocr_result['metadata'].get('ocr_confidence', 0),
            image_metadata=ocr_result.get('metadata', {})
        )
        
        db.add(image_record)
        db.flush()
        
        # Add to image FAISS store
        image_store = get_image_store(dimension=img_embedding.shape[0])
        faiss_indices = image_store.add_vectors(img_embedding.reshape(1, -1), [image_record.id])
        image_record.faiss_index = faiss_indices[0]
        
        # Also add OCR text to text store if available
        ocr_text = ocr_result.get('text', '').strip()
        if ocr_text:
            text_store = get_text_store(dimension=text_embedder.get_embedding_dimension())
            text_embedding = text_embedder.embed(ocr_text)
            
            chunk_record = DocumentChunk(
                document_id=document_id,
                chunk_index=0,
                content=ocr_text,
                chunk_metadata={'source': 'ocr', 'ocr_confidence': ocr_result['metadata'].get('ocr_confidence', 0)}
            )
            db.add(chunk_record)
            db.flush()
            
            faiss_indices = text_store.add_vectors(text_embedding, [chunk_record.id])
            chunk_record.faiss_index = faiss_indices[0]
        
        db.commit()
        
        logger.info(f"Processed image: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        db.rollback()
        return False


async def process_audio(document_id: str, file_path: str, filename: str, db: Session) -> bool:
    """Process audio document."""
    try:
        # Transcribe audio
        result = audio_processor.transcribe(file_path)
        
        if not result['success']:
            return False
        
        # Get FAISS store
        text_store = get_text_store(dimension=text_embedder.get_embedding_dimension())
        
        # Process segments
        chunk_records = []
        chunks = []
        
        for segment in result['segments']:
            chunk_record = DocumentChunk(
                document_id=document_id,
                chunk_index=segment['id'],
                content=segment['text'],
                timestamp=segment['timestamp'],
                start_time=segment['start'],
                end_time=segment['end'],
                chunk_metadata={'language': result['metadata'].get('language', 'unknown')}
            )
            chunk_records.append(chunk_record)
            chunks.append(segment['text'])
        
        # Generate embeddings
        embeddings = text_embedder.embed_batch(chunks)
        
        # Add to database
        db.add_all(chunk_records)
        db.flush()
        
        # Add to FAISS
        chunk_ids = [chunk.id for chunk in chunk_records]
        faiss_indices = text_store.add_vectors(embeddings, chunk_ids)
        
        # Update FAISS indices
        for chunk, faiss_idx in zip(chunk_records, faiss_indices):
            chunk.faiss_index = faiss_idx
        
        db.commit()
        
        logger.info(f"Processed audio: {filename} ({len(chunks)} segments)")
        return True
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        db.rollback()
        return False


@router.post("/batch")
async def upload_multiple_files(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """
    Upload multiple files at once.
    
    Args:
        files: List of uploaded files
        db: Database session
        
    Returns:
        List of upload responses
    """
    responses = []
    
    for file in files:
        try:
            response = await upload_file(file, db)
            responses.append(response)
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {str(e)}")
            responses.append(UploadResponse(
                success=False,
                message=str(e),
                document_id="",
                filename=file.filename,
                document_type=get_document_type(file.filename),
                processed=False
            ))
    
    return responses
