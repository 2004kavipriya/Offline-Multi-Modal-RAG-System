"""
Text embedding generator using sentence-transformers.
Generates embeddings for text chunks for semantic search.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TextEmbedder:
    """Generate embeddings for text using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the text embedder.
        
        Args:
            model_name: Name of the sentence-transformer model
                       Options: all-MiniLM-L6-v2 (fast), all-mpnet-base-v2 (quality)
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = None
        logger.info(f"TextEmbedder initialized with model: {model_name}")
    
    def load_model(self):
        """Load the sentence-transformer model."""
        if self.model is None:
            logger.info(f"Loading text embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def embed(self, text: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Generate embeddings for text.
        
        Args:
            text: Single text string or list of text strings
            normalize: Whether to normalize embeddings (for cosine similarity)
            
        Returns:
            Numpy array of embeddings
        """
        try:
            # Load model if not already loaded
            self.load_model()
            
            # Convert single string to list
            if isinstance(text, str):
                text = [text]
            
            # Generate embeddings
            embeddings = self.model.encode(
                text,
                normalize_embeddings=normalize,
                show_progress_bar=False
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating text embeddings: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 32, normalize: bool = True) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            normalize: Whether to normalize embeddings
            
        Returns:
            Numpy array of embeddings
        """
        try:
            self.load_model()
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=len(texts) > 100
            )
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension
        """
        if self.embedding_dim is None:
            self.load_model()
        return self.embedding_dim
    
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
