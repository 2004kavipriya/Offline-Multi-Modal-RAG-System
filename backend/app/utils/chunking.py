"""
Text chunking utilities for splitting documents into manageable pieces.
"""

from typing import List, Dict, Any
import re


class TextChunker:
    """Split text into chunks for embedding and retrieval."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        chunk_id = 0
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence or word boundary
            if end < text_length:
                # Look for sentence boundary (. ! ?)
                sentence_end = max(
                    text.rfind('. ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('? ', start, end)
                )
                
                if sentence_end > start:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    space = text.rfind(' ', start, end)
                    if space > start:
                        end = space
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk = {
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'start_char': start,
                    'end_char': end,
                }
                
                if metadata:
                    chunk['metadata'] = metadata.copy()
                
                chunks.append(chunk)
                chunk_id += 1
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            
            # Ensure we make progress
            if start <= chunks[-1]['start_char'] if chunks else 0:
                start = end
        
        return chunks
    
    def chunk_by_sentences(self, text: str, max_sentences: int = 5) -> List[str]:
        """
        Split text into chunks by sentences.
        
        Args:
            text: Text to chunk
            max_sentences: Maximum sentences per chunk
            
        Returns:
            List of text chunks
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        
        for sentence in sentences:
            current_chunk.append(sentence)
            
            if len(current_chunk) >= max_sentences:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        
        # Add remaining sentences
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str, max_paragraphs: int = 3) -> List[str]:
        """
        Split text into chunks by paragraphs.
        
        Args:
            text: Text to chunk
            max_paragraphs: Maximum paragraphs per chunk
            
        Returns:
            List of text chunks
        """
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        
        for paragraph in paragraphs:
            current_chunk.append(paragraph)
            
            if len(current_chunk) >= max_paragraphs:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
        
        # Add remaining paragraphs
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def smart_chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Intelligently chunk text based on structure.
        Tries to preserve semantic units (paragraphs, sentences).
        
        Args:
            text: Text to chunk
            metadata: Optional metadata
            
        Returns:
            List of chunk dictionaries
        """
        # First try paragraph-based chunking
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                # Save current chunk
                chunk = {
                    'chunk_id': chunk_id,
                    'text': current_chunk.strip(),
                }
                if metadata:
                    chunk['metadata'] = metadata.copy()
                chunks.append(chunk)
                chunk_id += 1
                current_chunk = ""
            
            # If single paragraph is too large, split it
            if len(paragraph) > self.chunk_size:
                # Split large paragraph into smaller chunks
                para_chunks = self.chunk_text(paragraph, metadata)
                for pc in para_chunks:
                    pc['chunk_id'] = chunk_id
                    chunks.append(pc)
                    chunk_id += 1
            else:
                current_chunk += paragraph + "\n\n"
        
        # Add remaining text
        if current_chunk.strip():
            chunk = {
                'chunk_id': chunk_id,
                'text': current_chunk.strip(),
            }
            if metadata:
                chunk['metadata'] = metadata.copy()
            chunks.append(chunk)
        
        return chunks
