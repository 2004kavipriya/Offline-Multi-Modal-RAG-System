"""
Image processor with OCR and CLIP embeddings.
Extracts text from images and generates embeddings for semantic search.
"""

from PIL import Image
import pytesseract
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Process images with OCR and generate embeddings."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the image processor.
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from an image using OCR.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing OCR text and metadata
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {file_path}")
            
            # Open image
            image = Image.open(file_path)
            
            # Extract metadata
            metadata = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height,
            }
            
            # Perform OCR
            ocr_text = pytesseract.image_to_string(image)
            
            # Get detailed OCR data with bounding boxes
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract confidence scores
            confidences = [conf for conf in ocr_data['conf'] if conf != -1]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            metadata['ocr_confidence'] = avg_confidence
            metadata['num_words'] = len([w for w in ocr_data['text'] if w.strip()])
            
            logger.info(f"Extracted text from image {path.name} with {avg_confidence:.2f}% confidence")
            
            return {
                'text': ocr_text.strip(),
                'metadata': metadata,
                'ocr_data': ocr_data,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            return {
                'text': '',
                'metadata': {},
                'ocr_data': {},
                'success': False,
                'error': str(e)
            }
    
    def get_image_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic image information without OCR.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing image metadata
        """
        try:
            image = Image.open(file_path)
            
            return {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting image info for {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def preprocess_image(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Preprocess image for better OCR results.
        
        Args:
            file_path: Path to the input image
            output_path: Path to save preprocessed image (optional)
            
        Returns:
            Path to the preprocessed image
        """
        try:
            image = Image.open(file_path)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Increase contrast (simple approach)
            # For more advanced preprocessing, use OpenCV
            
            if output_path:
                image.save(output_path)
                return output_path
            else:
                # Save to temp location
                temp_path = Path(file_path).parent / f"preprocessed_{Path(file_path).name}"
                image.save(temp_path)
                return str(temp_path)
                
        except Exception as e:
            logger.error(f"Error preprocessing image {file_path}: {str(e)}")
            return file_path
