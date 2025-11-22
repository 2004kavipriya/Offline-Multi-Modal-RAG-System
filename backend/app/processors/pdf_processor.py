"""
PDF document processor.
Extracts text from PDF files with page tracking for citations.
"""

import PyPDF2
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF documents and extract text with metadata."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        pass
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            pages_text = []
            metadata = {}
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                    }
                
                # Extract text from each page
                num_pages = len(pdf_reader.pages)
                metadata['num_pages'] = num_pages
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        pages_text.append({
                            'page_number': page_num + 1,
                            'text': text.strip()
                        })
            
            logger.info(f"Extracted text from {num_pages} pages in {path.name}")
            
            return {
                'pages': pages_text,
                'metadata': metadata,
                'total_pages': num_pages,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return {
                'pages': [],
                'metadata': {},
                'total_pages': 0,
                'success': False,
                'error': str(e)
            }
    
    def extract_text_by_page(self, file_path: str, page_number: int) -> str:
        """
        Extract text from a specific page.
        
        Args:
            file_path: Path to the PDF file
            page_number: Page number (1-indexed)
            
        Returns:
            Extracted text from the page
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if page_number < 1 or page_number > len(pdf_reader.pages):
                    raise ValueError(f"Invalid page number: {page_number}")
                
                page = pdf_reader.pages[page_number - 1]
                return page.extract_text().strip()
                
        except Exception as e:
            logger.error(f"Error extracting page {page_number} from {file_path}: {str(e)}")
            return ""
