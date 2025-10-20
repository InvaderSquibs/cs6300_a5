"""
Vector Database Populator

This module provides functionality to populate vector databases with embeddings
for both local and hosted solutions.
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDBBackend(ABC):
    """Abstract base class for vector database backends."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the vector database backend."""
        pass
    
    @abstractmethod
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """Add vectors with metadata to the database."""
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        pass


class ChromaDBBackend(VectorDBBackend):
    """ChromaDB backend implementation."""
    
    def __init__(self):
        self.client = None
        self.collection = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            self.client = chromadb.Client()
            collection_name = config.get('collection_name', 'default_collection')
            
            # Try to get existing collection or create new one
            try:
                self.collection = self.client.get_collection(collection_name)
                logger.info(f"Connected to existing ChromaDB collection: {collection_name}")
            except Exception:
                self.collection = self.client.create_collection(collection_name)
                logger.info(f"Created new ChromaDB collection: {collection_name}")
                
        except ImportError:
            raise ImportError("ChromaDB not installed. Run: pip install chromadb")
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """Add vectors with metadata to ChromaDB."""
        if self.collection is None:
            raise RuntimeError("ChromaDB not initialized")
        
        # Generate IDs for the vectors
        ids = [f"vec_{i}" for i in range(len(vectors))]
        
        # Convert numpy array to list for ChromaDB
        embeddings = vectors.tolist()
        
        self.collection.add(
            embeddings=embeddings,
            metadatas=metadata,
            ids=ids
        )
        logger.info(f"Added {len(vectors)} vectors to ChromaDB")
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors in ChromaDB."""
        if self.collection is None:
            raise RuntimeError("ChromaDB not initialized")
        
        results = self.collection.query(
            query_embeddings=[query_vector.tolist()],
            n_results=top_k
        )
        
        return [
            {
                'id': results['ids'][0][i],
                'distance': results['distances'][0][i],
                'metadata': results['metadatas'][0][i]
            }
            for i in range(len(results['ids'][0]))
        ]


class FAISSBackend(VectorDBBackend):
    """FAISS backend implementation for local vector storage."""
    
    def __init__(self):
        self.index = None
        self.metadata = []
        self.dimension = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize FAISS index."""
        try:
            import faiss
            self.dimension = config.get('dimension', 384)  # Default for sentence transformers
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info(f"Initialized FAISS index with dimension {self.dimension}")
        except ImportError:
            raise ImportError("FAISS not installed. Run: pip install faiss-cpu")
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """Add vectors with metadata to FAISS index."""
        if self.index is None:
            raise RuntimeError("FAISS not initialized")
        
        # Ensure vectors are float32 for FAISS
        vectors = vectors.astype(np.float32)
        
        self.index.add(vectors)
        self.metadata.extend(metadata)
        logger.info(f"Added {len(vectors)} vectors to FAISS index")
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors in FAISS index."""
        if self.index is None:
            raise RuntimeError("FAISS not initialized")
        
        query_vector = query_vector.astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                results.append({
                    'id': idx,
                    'distance': float(distance),
                    'metadata': self.metadata[idx]
                })
        
        return results


class VectorDBPopulator:
    """Main class for populating vector databases."""
    
    def __init__(self, backend_type: str = 'chromadb'):
        """
        Initialize the vector database populator.
        
        Args:
            backend_type: Type of backend ('chromadb' or 'faiss')
        """
        self.backend_type = backend_type
        self.backend = self._create_backend(backend_type)
        self.encoder = None
    
    def _create_backend(self, backend_type: str) -> VectorDBBackend:
        """Create the appropriate backend instance."""
        if backend_type.lower() == 'chromadb':
            return ChromaDBBackend()
        elif backend_type.lower() == 'faiss':
            return FAISSBackend()
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")
    
    def initialize_encoder(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the sentence transformer for encoding text."""
        try:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer(model_name)
            logger.info(f"Initialized encoder: {model_name}")
        except ImportError:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")
    
    def initialize_database(self, config: Dict[str, Any] = None):
        """Initialize the vector database backend."""
        if config is None:
            config = {}
        
        self.backend.initialize(config)
        logger.info(f"Initialized {self.backend_type} backend")
    
    def populate_from_texts(self, 
                          texts: List[str], 
                          metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Populate the vector database from a list of texts.
        
        Args:
            texts: List of text strings to encode and store
            metadata: Optional metadata for each text
        """
        if self.encoder is None:
            self.initialize_encoder()
        
        # Generate embeddings
        logger.info(f"Encoding {len(texts)} texts...")
        embeddings = self.encoder.encode(texts)
        
        # Prepare metadata
        if metadata is None:
            metadata = [{'text': text, 'index': i} for i, text in enumerate(texts)]
        elif len(metadata) != len(texts):
            raise ValueError("Metadata list length must match texts list length")
        
        # Add to database
        self.backend.add_vectors(embeddings, metadata)
        logger.info("Successfully populated vector database")
    
    def populate_from_vectors(self, 
                            vectors: np.ndarray, 
                            metadata: List[Dict[str, Any]]) -> None:
        """
        Populate the vector database from pre-computed vectors.
        
        Args:
            vectors: Pre-computed vector embeddings
            metadata: Metadata for each vector
        """
        if len(vectors) != len(metadata):
            raise ValueError("Vectors and metadata lists must have the same length")
        
        self.backend.add_vectors(vectors, metadata)
        logger.info(f"Successfully populated vector database with {len(vectors)} vectors")
    
    def search_similar(self, 
                      query: Union[str, np.ndarray], 
                      top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query: Text query or vector to search for
            top_k: Number of top results to return
            
        Returns:
            List of similar vectors with metadata
        """
        if isinstance(query, str):
            if self.encoder is None:
                self.initialize_encoder()
            query_vector = self.encoder.encode([query])[0]
        else:
            query_vector = query
        
        return self.backend.search(query_vector, top_k)


def create_sample_data() -> tuple[List[str], List[Dict[str, Any]]]:
    """Create sample data for testing the vector database population."""
    sample_texts = [
        "Machine learning is a subset of artificial intelligence.",
        "Natural language processing enables computers to understand human language.",
        "Deep learning uses neural networks with multiple layers.",
        "Computer vision allows machines to interpret visual information.",
        "Reinforcement learning trains agents through trial and error.",
        "Data science combines statistics, programming, and domain expertise.",
        "Cloud computing provides on-demand access to computing resources.",
        "Blockchain technology enables secure and decentralized transactions.",
        "Internet of Things connects everyday devices to the internet.",
        "Cybersecurity protects digital systems from threats and attacks."
    ]
    
    sample_metadata = [
        {"category": "AI/ML", "topic": "machine_learning", "source": "sample"},
        {"category": "AI/ML", "topic": "nlp", "source": "sample"},
        {"category": "AI/ML", "topic": "deep_learning", "source": "sample"},
        {"category": "AI/ML", "topic": "computer_vision", "source": "sample"},
        {"category": "AI/ML", "topic": "reinforcement_learning", "source": "sample"},
        {"category": "Data", "topic": "data_science", "source": "sample"},
        {"category": "Infrastructure", "topic": "cloud_computing", "source": "sample"},
        {"category": "Infrastructure", "topic": "blockchain", "source": "sample"},
        {"category": "Infrastructure", "topic": "iot", "source": "sample"},
        {"category": "Security", "topic": "cybersecurity", "source": "sample"}
    ]
    
    return sample_texts, sample_metadata


def main():
    """Example usage of the VectorDBPopulator."""
    # Create sample data
    texts, metadata = create_sample_data()
    
    # Initialize populator with ChromaDB backend
    populator = VectorDBPopulator(backend_type='chromadb')
    populator.initialize_database({'collection_name': 'sample_collection'})
    
    # Populate the database
    populator.populate_from_texts(texts, metadata)
    
    # Test search functionality
    query = "artificial intelligence and neural networks"
    results = populator.search_similar(query, top_k=3)
    
    print(f"\nSearch results for: '{query}'")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        print(f"{i}. Distance: {result['distance']:.4f}")
        print(f"   Metadata: {result['metadata']}")
        print()


if __name__ == "__main__":
    main()