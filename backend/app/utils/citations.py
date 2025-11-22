"""
Citation tracking and formatting utilities.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Citation:
    """Represents a citation to a source document."""
    citation_id: int
    document_id: str
    filename: str
    document_type: str
    excerpt: str
    relevance_score: float
    page_number: int = None
    timestamp: str = None
    metadata: Dict[str, Any] = None


class CitationManager:
    """Manage citations for RAG responses."""
    
    def __init__(self):
        """Initialize the citation manager."""
        self.citations = []
        self.citation_counter = 1
    
    def add_citation(
        self,
        document_id: str,
        filename: str,
        document_type: str,
        excerpt: str,
        relevance_score: float,
        page_number: int = None,
        timestamp: str = None,
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Add a citation and return its ID.
        
        Args:
            document_id: Unique document identifier
            filename: Source filename
            document_type: Type of document (pdf, docx, image, audio)
            excerpt: Relevant text excerpt
            relevance_score: Relevance score
            page_number: Page number (for PDFs)
            timestamp: Timestamp (for audio)
            metadata: Additional metadata
            
        Returns:
            Citation ID
        """
        citation = Citation(
            citation_id=self.citation_counter,
            document_id=document_id,
            filename=filename,
            document_type=document_type,
            excerpt=excerpt,
            relevance_score=relevance_score,
            page_number=page_number,
            timestamp=timestamp,
            metadata=metadata or {}
        )
        
        self.citations.append(citation)
        citation_id = self.citation_counter
        self.citation_counter += 1
        
        return citation_id
    
    def get_citation(self, citation_id: int) -> Citation:
        """
        Get a citation by ID.
        
        Args:
            citation_id: Citation ID
            
        Returns:
            Citation object or None
        """
        for citation in self.citations:
            if citation.citation_id == citation_id:
                return citation
        return None
    
    def get_all_citations(self) -> List[Citation]:
        """
        Get all citations.
        
        Returns:
            List of citations
        """
        return self.citations
    
    def format_citation(self, citation: Citation) -> str:
        """
        Format a citation for display.
        
        Args:
            citation: Citation object
            
        Returns:
            Formatted citation string
        """
        parts = [f"[{citation.citation_id}] {citation.filename}"]
        
        if citation.page_number:
            parts.append(f"(Page {citation.page_number})")
        
        if citation.timestamp:
            parts.append(f"({citation.timestamp})")
        
        return " ".join(parts)
    
    def format_all_citations(self) -> str:
        """
        Format all citations as a numbered list.
        
        Returns:
            Formatted citations string
        """
        if not self.citations:
            return ""
        
        formatted = ["Sources:"]
        for citation in self.citations:
            formatted.append(self.format_citation(citation))
        
        return "\n".join(formatted)
    
    def insert_citations_in_text(self, text: str, citation_map: Dict[str, int]) -> str:
        """
        Insert citation markers in text.
        
        Args:
            text: Original text
            citation_map: Mapping of text snippets to citation IDs
            
        Returns:
            Text with citation markers
        """
        result = text
        
        for snippet, citation_id in citation_map.items():
            # Replace snippet with snippet + citation marker
            result = result.replace(snippet, f"{snippet} [{citation_id}]")
        
        return result
    
    def reset(self):
        """Reset all citations."""
        self.citations = []
        self.citation_counter = 1
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """
        Convert citations to list of dictionaries.
        
        Returns:
            List of citation dictionaries
        """
        return [
            {
                'citation_id': c.citation_id,
                'document_id': c.document_id,
                'filename': c.filename,
                'document_type': c.document_type,
                'excerpt': c.excerpt,
                'relevance_score': c.relevance_score,
                'page_number': c.page_number,
                'timestamp': c.timestamp,
                'metadata': c.metadata
            }
            for c in self.citations
        ]
