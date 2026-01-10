"""
Embeddings Service
Converts text into vector representations for semantic search

Why embeddings?
- Enable semantic search (meaning-based, not keyword-based)
- Find similar content even with different words
- Core of RAG systems

Model: all-MiniLM-L6-v2
- Size: Only 80MB!
- Speed: Fast on CPU
- Quality: Great for semantic search
- Dimensions: 384 (perfect for ChromaDB)
"""

import os
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings.
    
    Features:
    - Batch processing for efficiency
    - Caching loaded model
    - Automatic device selection (GPU if available)
    - Normalized vectors for better similarity search
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedding service.
        
        Args:
            model_name: HuggingFace model name (default from .env)
        """
        
        # Get model name from env or use default
        if model_name is None:
            model_name = os.getenv(
                "EMBEDDING_MODEL",
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        
        self.model_name = model_name
        
        logger.info(f"Loading embedding model: {model_name}")
        
        try:
            # Load the model
            self.model = SentenceTransformer(model_name)
            
            # Get embedding dimension
            self.dimension = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"Model loaded successfully. Embedding dimension: {self.dimension}")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def generate_embedding(self, text: str, normalize: bool = True) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            normalize: Whether to normalize the vector (recommended for similarity)
            
        Returns:
            Embedding vector as list of floats
        """
        
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension
        
        try:
            # Generate embedding
            embedding = self.model.encode(
                text,
                normalize_embeddings=normalize,
                show_progress_bar=False
            )
            
            # Convert to list
            embedding_list = embedding.tolist()
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Much faster than generating one by one!
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            normalize: Whether to normalize vectors
            show_progress: Show progress bar
            
        Returns:
            List of embedding vectors
        """
        
        if not texts:
            logger.warning("Empty text list provided")
            return []
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Generate embeddings in batches
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            
            # Convert to list of lists
            embeddings_list = embeddings.tolist()
            
            logger.info(f"Successfully generated {len(embeddings_list)} embeddings")
            
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Returns value between -1 and 1:
        - 1: Identical vectors
        - 0: Orthogonal (no similarity)
        - -1: Opposite vectors
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score
        """
        
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            # (dot product of normalized vectors)
            similarity = np.dot(vec1, vec2)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return 0.0
    
    def find_most_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find most similar embeddings to query.
        
        Args:
            query_embedding: Query vector
            candidate_embeddings: List of candidate vectors
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        
        try:
            # Convert to numpy
            query = np.array(query_embedding)
            candidates = np.array(candidate_embeddings)
            
            # Compute similarities
            similarities = np.dot(candidates, query)
            
            # Get top k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Create result tuples
            results = [
                (int(idx), float(similarities[idx]))
                for idx in top_indices
            ]
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar embeddings: {str(e)}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension (e.g., 384 for MiniLM)
        """
        return self.dimension
    
    def test_embedding(self) -> bool:
        """
        Test if embedding generation works.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            test_text = "This is a test sentence for embedding."
            embedding = self.generate_embedding(test_text)
            
            # Verify embedding
            if len(embedding) == self.dimension:
                logger.info("Embedding test successful")
                return True
            else:
                logger.error(f"Embedding dimension mismatch: {len(embedding)} vs {self.dimension}")
                return False
                
        except Exception as e:
            logger.error(f"Embedding test failed: {str(e)}")
            return False


# Singleton instance (loaded once, reused throughout app)
_embedding_service_instance = None


def get_embedding_service() -> EmbeddingService:
    """
    Get singleton instance of EmbeddingService.
    
    This ensures we only load the model once and reuse it.
    Important for performance!
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service_instance
    
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    
    return _embedding_service_instance


# Example usage and testing
if __name__ == "__main__":
    # Test the embedding service
    print("🧪 Testing Embedding Service...")
    
    try:
        service = EmbeddingService()
        
        # Test single embedding
        print("\n1️⃣ Testing single embedding...")
        text = "Artificial intelligence is transforming the world."
        embedding = service.generate_embedding(text)
        
        print(f"✅ Generated embedding of dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        
        # Test batch embeddings
        print("\n2️⃣ Testing batch embeddings...")
        texts = [
            "Machine learning is a subset of AI.",
            "Deep learning uses neural networks.",
            "Natural language processing enables AI to understand text.",
            "Computer vision allows machines to see.",
            "Reinforcement learning learns through trial and error."
        ]
        
        embeddings = service.generate_embeddings(texts, show_progress=False)
        print(f"✅ Generated {len(embeddings)} embeddings")
        
        # Test similarity
        print("\n3️⃣ Testing similarity computation...")
        sim = service.compute_similarity(embeddings[0], embeddings[1])
        print(f"✅ Similarity between first two texts: {sim:.4f}")
        
        # Test finding similar
        print("\n4️⃣ Testing similarity search...")
        query = "What is neural network learning?"
        query_embedding = service.generate_embedding(query)
        
        similar = service.find_most_similar(
            query_embedding,
            embeddings,
            top_k=3
        )
        
        print(f"✅ Top 3 most similar texts to '{query}':")
        for idx, score in similar:
            print(f"   - Text {idx + 1} (score: {score:.4f}): {texts[idx][:60]}...")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")