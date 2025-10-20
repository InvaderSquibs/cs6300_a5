"""Unit tests for ChromaVectorDB."""

import pytest
from vector_template.database.chroma_client import ChromaVectorDB


class TestChromaVectorDB:
    """Test cases for ChromaVectorDB class."""
    
    def test_initialization(self, temp_db_dir):
        """Test database initialization."""
        db = ChromaVectorDB(
            persist_directory=temp_db_dir,
            collection_name="test_init"
        )
        assert db.collection_name == "test_init"
        assert db.persist_directory == temp_db_dir
    
    def test_add_documents(self, vector_db, sample_documents):
        """Test adding documents to the database."""
        vector_db.add_documents(sample_documents)
        info = vector_db.get_collection_info()
        assert info["count"] == len(sample_documents)
    
    def test_query_documents(self, vector_db, sample_documents):
        """Test querying documents."""
        # Add documents first
        vector_db.add_documents(sample_documents)
        
        # Query for pasta-related content
        results = vector_db.query("pasta cooking", n_results=2)
        
        assert "documents" in results
        assert len(results["documents"][0]) <= 2
        assert any("pasta" in doc.lower() for doc in results["documents"][0])
    
    def test_delete_documents(self, vector_db, sample_documents):
        """Test deleting documents."""
        # Add documents with specific IDs
        ids = ["doc1", "doc2", "doc3"]
        vector_db.add_documents(sample_documents, ids=ids)
        
        # Delete one document
        vector_db.delete_documents(["doc1"])
        
        # Check count
        info = vector_db.get_collection_info()
        assert info["count"] == 2
    
    def test_update_documents(self, vector_db):
        """Test updating documents."""
        # Add initial document
        vector_db.add_documents(["Initial content"], ids=["update_test"])
        
        # Update the document
        vector_db.update_documents(
            ids=["update_test"],
            documents=["Updated content"]
        )
        
        # Query to verify update
        results = vector_db.query("updated", n_results=1)
        assert "updated" in results["documents"][0][0].lower()
    
    def test_collection_operations(self, vector_db):
        """Test collection management operations."""
        # Test getting collection info
        info = vector_db.get_collection_info()
        assert "name" in info
        assert "count" in info
        
        # Test listing collections
        collections = vector_db.list_collections()
        assert isinstance(collections, list)
        assert vector_db.collection_name in collections
        
        # Test creating new collection
        vector_db.create_collection("new_test_collection")
        collections = vector_db.list_collections()
        assert "new_test_collection" in collections
    
    def test_reset_collection(self, vector_db, sample_documents):
        """Test resetting a collection."""
        # Add documents
        vector_db.add_documents(sample_documents)
        info = vector_db.get_collection_info()
        assert info["count"] > 0
        
        # Reset collection
        vector_db.reset_collection()
        info = vector_db.get_collection_info()
        assert info["count"] == 0
    
    def test_query_with_metadata_filter(self, vector_db):
        """Test querying with metadata filters."""
        # Add documents with metadata
        documents = ["Italian pasta dish", "Indian curry recipe"]
        metadatas = [{"cuisine": "Italian"}, {"cuisine": "Indian"}]
        ids = ["italian_doc", "indian_doc"]
        
        vector_db.add_documents(documents, metadatas=metadatas, ids=ids)
        
        # Query with metadata filter
        results = vector_db.query(
            "recipe",
            n_results=2,
            where={"cuisine": "Italian"}
        )
        
        assert len(results["documents"][0]) == 1
        assert "pasta" in results["documents"][0][0].lower()
    
    def test_empty_query(self, vector_db):
        """Test querying an empty collection."""
        results = vector_db.query("anything", n_results=5)
        assert results["documents"] == [[]]
        assert results["metadatas"] == [[]]
        assert results["distances"] == [[]]