import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import logging
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize CLIP for image embeddings
try:
    # Use local_files_only=False to download if needed, and trust_remote_code for safety
    clip_model = CLIPModel.from_pretrained(
        "openai/clip-vit-base-patch32",
        use_safetensors=True  # Use safe tensors to avoid security vulnerability
    )
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    clip_model.to(device)
    logger.info(f"CLIP model loaded successfully on {device}")
except Exception as e:
    logger.error(f"Could not load CLIP model: {e}")
    clip_model = None
    clip_processor = None

# FAISS index for text embeddings
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 dimension
faiss_index = faiss.IndexFlatIP(EMBEDDING_DIM)  # Inner product for cosine similarity
index_to_chunk_map = []  # Maps FAISS index to (doc_id, chunk_index)

# FAISS index for image embeddings (CLIP)
IMAGE_EMBEDDING_DIM = 512  # CLIP dimension
image_faiss_index = faiss.IndexFlatIP(IMAGE_EMBEDDING_DIM)
image_index_to_doc_map = []  # Maps image index to doc_id


def generate_embedding(text: str) -> list:
    """Generate embeddings for text."""
    embedding = model.encode(text)
    return embedding.tolist()


def generate_image_embedding(image_path: str) -> list:
    """Generate embeddings for images using CLIP."""
    if clip_model is None or clip_processor is None:
        raise ValueError("CLIP model not available. Please install transformers and torch.")
    
    try:
        # Load and process image
        image = Image.open(image_path).convert("RGB")
        inputs = clip_processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate embedding
        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
            # Normalize
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features.cpu().numpy()[0].tolist()
    except Exception as e:
        logger.error(f"Error generating image embedding: {e}")
        raise


def add_chunks_to_index(doc_id: int, chunks: list[dict]):
    """Add document chunks to FAISS index."""
    global faiss_index, index_to_chunk_map
    
    embeddings = []
    for chunk in chunks:
        embedding = generate_embedding(chunk["content"])
        embeddings.append(embedding)
        index_to_chunk_map.append({
            "doc_id": doc_id,
            "chunk_index": chunk["chunk_index"],
            "content": chunk["content"]
        })
    
    if embeddings:
        embeddings_array = np.array(embeddings)
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        embeddings_array = embeddings_array / norms
        faiss_index.add(embeddings_array.astype('float32'))
        logger.info(f"Added {len(embeddings)} chunks to FAISS index")


def add_image_to_index(doc_id: int, image_path: str):
    """Add image embedding to FAISS index."""
    global image_faiss_index, image_index_to_doc_map
    
    try:
        # Generate CLIP embedding
        embedding = generate_image_embedding(image_path)
        embedding_array = np.array([embedding])
        
        # Normalize for cosine similarity
        norm = np.linalg.norm(embedding_array, axis=1, keepdims=True)
        embedding_array = embedding_array / norm
        
        # Add to index
        image_faiss_index.add(embedding_array.astype('float32'))
        image_index_to_doc_map.append({"doc_id": doc_id})
        
        logger.info(f"Added image embedding for doc_id {doc_id} to image index")
    except Exception as e:
        logger.error(f"Error adding image to index: {e}")


def search_similar_images(query_image_path: str, top_k: int = 10) -> list[dict]:
    """Search for similar images using CLIP embeddings."""
    if image_faiss_index.ntotal == 0:
        return []
    
    try:
        # Generate query embedding
        query_embedding = np.array([generate_image_embedding(query_image_path)])
        # Normalize
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Search
        distances, indices = image_faiss_index.search(
            query_embedding.astype('float32'), 
            min(top_k, image_faiss_index.ntotal)
        )
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(image_index_to_doc_map):
                doc_info = image_index_to_doc_map[idx]
                results.append({
                    "doc_id": doc_info["doc_id"],
                    "similarity": float(dist)
                })
        
        return results
    except Exception as e:
        logger.error(f"Error searching similar images: {e}")
        return []


def search_similar_chunks(query: str, top_k: int = 5, filter_doc_ids: list[int] = None) -> list[dict]:
    """Search for similar chunks using FAISS.
    
    Args:
        query: Search query text
        top_k: Number of results to return
        filter_doc_ids: Optional list of document IDs to filter results
    """
    if faiss_index.ntotal == 0:
        return []
    
    # Generate query embedding
    query_embedding = np.array([generate_embedding(query)])
    # Normalize
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    
    # If filtering by document, we need to search more to account for filtering
    search_k = top_k * 3 if filter_doc_ids else top_k
    
    # Search
    distances, indices = faiss_index.search(query_embedding.astype('float32'), min(search_k, faiss_index.ntotal))
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(index_to_chunk_map):
            chunk_info = index_to_chunk_map[idx]
            
            # Apply document filter if specified
            if filter_doc_ids and chunk_info["doc_id"] not in filter_doc_ids:
                continue
            
            results.append({
                "doc_id": chunk_info["doc_id"],
                "chunk_index": chunk_info["chunk_index"],
                "content": chunk_info["content"],
                "similarity": float(dist)
            })
            
            # Stop when we have enough filtered results
            if len(results) >= top_k:
                break
    
    return results


def get_index_stats() -> dict:
    """Get FAISS index statistics."""
    return {
        "total_vectors": faiss_index.ntotal,
        "dimension": EMBEDDING_DIM,
        "total_chunks": len(index_to_chunk_map)
    }


def save_state(directory: Path):
    """Save FAISS indices and maps to disk."""
    directory.mkdir(parents=True, exist_ok=True)
    
    # Save text FAISS index
    faiss.write_index(faiss_index, str(directory / "faiss_index.bin"))
    
    # Save text chunk map
    with open(directory / "chunk_map.pkl", "wb") as f:
        pickle.dump(index_to_chunk_map, f)
    
    # Save image FAISS index
    faiss.write_index(image_faiss_index, str(directory / "image_faiss_index.bin"))
    
    # Save image doc map
    with open(directory / "image_doc_map.pkl", "wb") as f:
        pickle.dump(image_index_to_doc_map, f)
        
    logger.info(f"Saved FAISS indices (text: {faiss_index.ntotal} vectors, images: {image_faiss_index.ntotal} vectors)")


def load_state(directory: Path):
    """Load FAISS indices and maps from disk."""
    global faiss_index, index_to_chunk_map, image_faiss_index, image_index_to_doc_map
    
    try:
        # Load text index
        if (directory / "faiss_index.bin").exists():
            faiss_index = faiss.read_index(str(directory / "faiss_index.bin"))
            logger.info(f"Loaded text FAISS index with {faiss_index.ntotal} vectors")
            
        # Load text chunk map
        if (directory / "chunk_map.pkl").exists():
            with open(directory / "chunk_map.pkl", "rb") as f:
                index_to_chunk_map = pickle.load(f)
            logger.info(f"Loaded chunk map with {len(index_to_chunk_map)} entries")
        
        # Load image index
        if (directory / "image_faiss_index.bin").exists():
            image_faiss_index = faiss.read_index(str(directory / "image_faiss_index.bin"))
            logger.info(f"Loaded image FAISS index with {image_faiss_index.ntotal} vectors")
        
        # Load image doc map
        if (directory / "image_doc_map.pkl").exists():
            with open(directory / "image_doc_map.pkl", "rb") as f:
                image_index_to_doc_map = pickle.load(f)
            logger.info(f"Loaded image doc map with {len(image_index_to_doc_map)} entries")
            
    except Exception as e:
        logger.error(f"Error loading embedding state: {e}")
