"""
FAISS vector store for semantic search.
Manages document embeddings and retrieval.
"""

import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pickle
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class FAISSStore:
    """FAISS vector store for semantic search."""
    
    def __init__(self, index_name: str = "documents", dimension: int = 384):
        """
        Initialize FAISS store.
        
        Args:
            index_name: Name of the index
            dimension: Embedding dimension
        """
        settings = get_settings()
        self.index_name = index_name
        self.dimension = dimension
        self.index_dir = Path(settings.faiss_index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.index_dir / f"{index_name}.index"
        self.metadata_path = self.index_dir / f"{index_name}_metadata.pkl"
        
        self.index = None
        self.id_to_index = {}  # Maps chunk IDs to FAISS indices
        self.index_to_id = {}  # Maps FAISS indices to chunk IDs
        self.next_index = 0
        
        self._load_or_create_index()
        
        logger.info(f"FAISS store initialized: {index_name} (dim={dimension})")
    
    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        if self.index_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                
                # Load metadata
                if self.metadata_path.exists():
                    with open(self.metadata_path, 'rb') as f:
                        metadata = pickle.load(f)
                        self.id_to_index = metadata.get('id_to_index', {})
                        self.index_to_id = metadata.get('index_to_id', {})
                        self.next_index = metadata.get('next_index', 0)
                
                logger.info(f"Loaded existing FAISS index: {self.index_name} ({self.index.ntotal} vectors)")
            except Exception as e:
                logger.error(f"Error loading FAISS index: {str(e)}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        # Using IndexFlatIP for cosine similarity (with normalized vectors)
        # For larger datasets, consider IndexIVFFlat or IndexHNSWFlat
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_to_index = {}
        self.index_to_id = {}
        self.next_index = 0
        logger.info(f"Created new FAISS index: {self.index_name}")
    
    def add_vectors(self, vectors: np.ndarray, ids: List[str]) -> List[int]:
        """
        Add vectors to the index.
        
        Args:
            vectors: Numpy array of vectors (shape: [n, dimension])
            ids: List of chunk IDs
            
        Returns:
            List of FAISS indices
        """
        if len(vectors) != len(ids):
            raise ValueError("Number of vectors must match number of IDs")
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        # Add to index
        self.index.add(vectors)
        
        # Track mappings
        faiss_indices = []
        for chunk_id in ids:
            faiss_idx = self.next_index
            self.id_to_index[chunk_id] = faiss_idx
            self.index_to_id[faiss_idx] = chunk_id
            faiss_indices.append(faiss_idx)
            self.next_index += 1
        
        logger.info(f"Added {len(vectors)} vectors to FAISS index")
        
        # Save index
        self.save()
        
        return faiss_indices
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector (shape: [dimension])
            top_k: Number of results to return
            
        Returns:
            List of (chunk_id, similarity_score) tuples
        """
        if self.index.ntotal == 0:
            return []
        
        # Normalize query vector
        query_vector = query_vector.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # Search
        distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        # Convert to results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1 and idx in self.index_to_id:
                chunk_id = self.index_to_id[idx]
                similarity = float(distance)  # Already cosine similarity with normalized vectors
                results.append((chunk_id, similarity))
        
        return results
    
    def search_batch(self, query_vectors: np.ndarray, top_k: int = 5) -> List[List[Tuple[str, float]]]:
        """
        Search for multiple query vectors.
        
        Args:
            query_vectors: Query vectors (shape: [n, dimension])
            top_k: Number of results per query
            
        Returns:
            List of result lists
        """
        if self.index.ntotal == 0:
            return [[] for _ in range(len(query_vectors))]
        
        # Normalize query vectors
        query_vectors = query_vectors.astype('float32')
        faiss.normalize_L2(query_vectors)
        
        # Search
        distances, indices = self.index.search(query_vectors, min(top_k, self.index.ntotal))
        
        # Convert to results
        all_results = []
        for query_distances, query_indices in zip(distances, indices):
            results = []
            for idx, distance in zip(query_indices, query_distances):
                if idx != -1 and idx in self.index_to_id:
                    chunk_id = self.index_to_id[idx]
                    similarity = float(distance)
                    results.append((chunk_id, similarity))
            all_results.append(results)
        
        return all_results
    
    def remove_vectors(self, ids: List[str]):
        """
        Remove vectors by IDs.
        Note: FAISS doesn't support efficient deletion, so we rebuild the index.
        
        Args:
            ids: List of chunk IDs to remove
        """
        # Get indices to keep
        indices_to_remove = set(self.id_to_index.get(id, -1) for id in ids)
        indices_to_keep = [idx for idx in range(self.index.ntotal) if idx not in indices_to_remove]
        
        if not indices_to_keep:
            # All vectors removed, create new index
            self._create_new_index()
            self.save()
            return
        
        # Reconstruct vectors to keep
        vectors_to_keep = np.zeros((len(indices_to_keep), self.dimension), dtype='float32')
        for i, idx in enumerate(indices_to_keep):
            vectors_to_keep[i] = self.index.reconstruct(idx)
        
        # Create new index
        self._create_new_index()
        
        # Re-add vectors
        new_ids = [self.index_to_id[idx] for idx in indices_to_keep]
        self.add_vectors(vectors_to_keep, new_ids)
        
        logger.info(f"Removed {len(ids)} vectors from FAISS index")
    
    def save(self):
        """Save the index and metadata to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            metadata = {
                'id_to_index': self.id_to_index,
                'index_to_id': self.index_to_id,
                'next_index': self.next_index
            }
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.debug(f"Saved FAISS index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'index_name': self.index_name,
            'dimension': self.dimension,
            'total_vectors': self.index.ntotal,
            'next_index': self.next_index
        }


# Global FAISS stores
_text_store = None
_image_store = None


def get_text_store(dimension: int = 384) -> FAISSStore:
    """Get the global text FAISS store."""
    global _text_store
    if _text_store is None:
        _text_store = FAISSStore(index_name="text_embeddings", dimension=dimension)
    return _text_store


def get_image_store(dimension: int = 512) -> FAISSStore:
    """Get the global image FAISS store."""
    global _image_store
    if _image_store is None:
        _image_store = FAISSStore(index_name="image_embeddings", dimension=dimension)
    return _image_store
