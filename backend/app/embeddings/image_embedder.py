"""
Image embedding generator using CLIP.
Generates embeddings for images that are compatible with text embeddings.
"""

from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from typing import List, Union
import torch
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ImageEmbedder:
    """Generate embeddings for images using CLIP."""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """
        Initialize the image embedder.
        
        Args:
            model_name: Name of the CLIP model
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"ImageEmbedder initialized with model: {model_name}, device: {self.device}")
    
    def load_model(self):
        """Load the CLIP model and processor."""
        if self.model is None:
            logger.info(f"Loading CLIP model: {self.model_name}")
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("CLIP model loaded successfully")
    
    def embed_image(self, image_path: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for an image.
        
        Args:
            image_path: Path to the image file
            normalize: Whether to normalize the embedding
            
        Returns:
            Numpy array of the image embedding
        """
        try:
            self.load_model()
            
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            
            # Convert to numpy
            embedding = image_features.cpu().numpy()[0]
            
            # Normalize if requested
            if normalize:
                embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating image embedding for {image_path}: {str(e)}")
            raise
    
    def embed_text(self, text: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Generate CLIP text embeddings (compatible with image embeddings).
        
        Args:
            text: Single text string or list of text strings
            normalize: Whether to normalize embeddings
            
        Returns:
            Numpy array of text embeddings
        """
        try:
            self.load_model()
            
            # Convert single string to list
            if isinstance(text, str):
                text = [text]
            
            # Process text
            inputs = self.processor(text=text, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embeddings
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
            
            # Convert to numpy
            embeddings = text_features.cpu().numpy()
            
            # Normalize if requested
            if normalize:
                embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            return embeddings if len(text) > 1 else embeddings[0]
            
        except Exception as e:
            logger.error(f"Error generating CLIP text embeddings: {str(e)}")
            raise
    
    def embed_images_batch(self, image_paths: List[str], normalize: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple images.
        
        Args:
            image_paths: List of image file paths
            normalize: Whether to normalize embeddings
            
        Returns:
            Numpy array of image embeddings
        """
        try:
            self.load_model()
            
            embeddings = []
            for image_path in image_paths:
                embedding = self.embed_image(image_path, normalize=normalize)
                embeddings.append(embedding)
            
            logger.info(f"Generated embeddings for {len(image_paths)} images")
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"Error generating batch image embeddings: {str(e)}")
            raise
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score
        """
        # Ensure embeddings are normalized
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        return float(np.dot(embedding1, embedding2))
    
    def image_text_similarity(self, image_path: str, text: str) -> float:
        """
        Calculate similarity between an image and text.
        
        Args:
            image_path: Path to the image
            text: Text string
            
        Returns:
            Similarity score
        """
        image_embedding = self.embed_image(image_path)
        text_embedding = self.embed_text(text)
        
        return self.similarity(image_embedding, text_embedding)
