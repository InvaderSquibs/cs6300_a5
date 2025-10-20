"""
Example usage script for the vector database populator.
"""

from src.vector_db_populator import VectorDBPopulator, create_sample_data
from src.config import get_config
import sys


def example_chromadb():
    """Example using ChromaDB backend."""
    print("=== ChromaDB Example ===")
    
    # Initialize populator
    populator = VectorDBPopulator(backend_type='chromadb')
    populator.initialize_database({'collection_name': 'example_collection'})
    
    # Create and populate with sample data
    texts, metadata = create_sample_data()
    populator.populate_from_texts(texts, metadata)
    
    # Search example
    query = "machine learning and artificial intelligence"
    results = populator.search_similar(query, top_k=3)
    
    print(f"\nSearch query: '{query}'")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        print(f"{i}. Distance: {result['distance']:.4f}")
        print(f"   Topic: {result['metadata']['topic']}")
        print(f"   Category: {result['metadata']['category']}")
        print()


def example_faiss():
    """Example using FAISS backend."""
    print("=== FAISS Example ===")
    
    # Initialize populator
    populator = VectorDBPopulator(backend_type='faiss')
    populator.initialize_database({'dimension': 384})
    
    # Create and populate with sample data
    texts, metadata = create_sample_data()
    populator.populate_from_texts(texts, metadata)
    
    # Search example
    query = "cybersecurity and data protection"
    results = populator.search_similar(query, top_k=3)
    
    print(f"\nSearch query: '{query}'")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        print(f"{i}. Distance: {result['distance']:.4f}")
        print(f"   Topic: {result['metadata']['topic']}")
        print(f"   Category: {result['metadata']['category']}")
        print()


def main():
    """Run examples based on command line argument."""
    if len(sys.argv) > 1:
        backend = sys.argv[1].lower()
        if backend == 'chromadb':
            example_chromadb()
        elif backend == 'faiss':
            example_faiss()
        else:
            print("Usage: python examples.py [chromadb|faiss]")
            print("Running both examples...")
            example_chromadb()
            print("\n" + "="*60 + "\n")
            example_faiss()
    else:
        print("Running both ChromaDB and FAISS examples...")
        example_chromadb()
        print("\n" + "="*60 + "\n")
        example_faiss()


if __name__ == "__main__":
    main()