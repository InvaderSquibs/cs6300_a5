"""
Simple usage example for the Vector Database Template.

This example shows how to use pre-computed vectors when you don't have
internet access for downloading embedding models.
"""

import numpy as np
from src.vector_db_populator import VectorDBPopulator

# Example: Using pre-computed vectors
def example_with_precomputed_vectors():
    """Example using pre-computed vectors (offline-friendly)."""
    
    # Simulate having pre-computed embeddings
    texts = [
        "Machine learning is powerful",
        "AI helps solve complex problems", 
        "Data science drives insights",
        "Neural networks learn patterns"
    ]
    
    # In real usage, these would come from a model like sentence-transformers
    # For this example, we use random vectors
    vectors = np.random.rand(len(texts), 384).astype(np.float32)
    
    metadata = [
        {"text": text, "index": i, "category": "AI"}
        for i, text in enumerate(texts)
    ]
    
    # Use FAISS backend (works offline)
    populator = VectorDBPopulator(backend_type='faiss')
    populator.initialize_database({'dimension': 384})
    
    # Populate the database
    populator.populate_from_vectors(vectors, metadata)
    print(f"Populated database with {len(vectors)} vectors")
    
    # Search using a query vector
    query_vector = np.random.rand(384).astype(np.float32)
    results = populator.search_similar(query_vector, top_k=2)
    
    print("\nSearch results:")
    for result in results:
        print(f"- {result['metadata']['text']} (distance: {result['distance']:.4f})")


if __name__ == "__main__":
    example_with_precomputed_vectors()
