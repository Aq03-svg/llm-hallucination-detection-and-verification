from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from config.settings import settings
from utils.logger import logger

class EmbeddingManager:
    """Manages semantic embeddings and similarity calculations."""
    
    def __init__(self, model_name: str = None):
        """Initialize the embedding model."""
        self.model_name = model_name or settings.EMBEDDING_MODEL
        try:
            self.model = SentenceTransformer(self.model_name, device=settings.DEVICE)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
        
        self.embedding_cache = {}
    
    def encode(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Encode text into embeddings."""
        if use_cache and text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            if use_cache and settings.ENABLE_CACHING:
                self.embedding_cache[text] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise
    
    def encode_batch(self, texts: List[str], use_cache: bool = True) -> List[np.ndarray]:
        """Encode multiple texts into embeddings."""
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Collect uncached texts
        for idx, text in enumerate(texts):
            if use_cache and text in self.embedding_cache:
                embeddings.append(self.embedding_cache[text])
            else:
                uncached_texts.append(text)
                uncached_indices.append(idx)
        
        # Encode uncached texts in batch
        if uncached_texts:
            try:
                batch_embeddings = self.model.encode(uncached_texts, convert_to_numpy=True)
                
                # Insert batch embeddings back in order
                for i, idx in enumerate(uncached_indices):
                    embeddings.insert(idx, batch_embeddings[i])
                    if use_cache and settings.ENABLE_CACHING:
                        self.embedding_cache[uncached_texts[i]] = batch_embeddings[i]
            except Exception as e:
                logger.error(f"Failed to encode batch: {e}")
                raise
        
        return embeddings
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        
        # Cosine similarity (1 - cosine_distance)
        similarity = 1 - cosine(emb1, emb2)
        return float(similarity)
    
    def similarity_batch(self, text1: str, texts2: List[str]) -> List[float]:
        """Calculate similarity between one text and multiple texts."""
        emb1 = self.encode(text1)
        emb2_list = self.encode_batch(texts2)
        
        similarities = [1 - cosine(emb1, emb2) for emb2 in emb2_list]
        return similarities
    
    def most_similar(self, text: str, candidates: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """Find most similar texts from candidates."""
        similarities = self.similarity_batch(text, candidates)
        ranked = sorted(zip(candidates, similarities), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
    
    def clear_cache(self):
        """Clear embedding cache."""
        self.embedding_cache.clear()
        logger.info("Embedding cache cleared")
