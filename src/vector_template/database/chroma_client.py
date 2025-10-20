"""Chroma vector database client implementation."""

from typing import Any, Dict, List, Optional, Union
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging

logger = logging.getLogger(__name__)


class ChromaVectorDB:
    """
    A wrapper class for ChromaDB to handle vector database operations.
    
    This class provides a simplified interface for common vector database operations
    including document storage, similarity search, and collection management.
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "default_collection",
        embedding_function: Optional[Any] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Initialize the ChromaVectorDB client.
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
            embedding_function: Custom embedding function, defaults to sentence-transformers
            host: Host for Chroma server (if using client-server mode)
            port: Port for Chroma server (if using client-server mode)
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Setup embedding function
        if embedding_function is None:
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        else:
            self.embedding_function = embedding_function
        
        # Initialize client
        if host and port:
            # Client-server mode
            self.client = chromadb.HttpClient(host=host, port=port)
            logger.info(f"Connected to Chroma server at {host}:{port}")
        else:
            # Local persistent mode
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info(f"Initialized local Chroma client with persistence at {persist_directory}")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        logger.info(f"Using collection: {collection_name}")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document texts to add
            metadatas: Optional list of metadata dictionaries for each document
            ids: Optional list of IDs for each document (auto-generated if not provided)
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in documents]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(documents)} documents to collection {self.collection_name}")
    
    def query(
        self,
        query_texts: Union[str, List[str]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Query the vector database for similar documents.
        
        Args:
            query_texts: Text(s) to search for
            n_results: Number of results to return
            where: Optional metadata filter
            include: What to include in results (documents, metadatas, distances, embeddings)
            
        Returns:
            Query results from ChromaDB
        """
        if isinstance(query_texts, str):
            query_texts = [query_texts]
        
        if include is None:
            include = ["documents", "metadatas", "distances"]
        
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            include=include
        )
        
        logger.info(f"Queried collection {self.collection_name} with {len(query_texts)} queries")
        return results
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents from the collection.
        
        Args:
            ids: List of document IDs to delete
        """
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from collection {self.collection_name}")
    
    def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Update existing documents in the collection.
        
        Args:
            ids: List of document IDs to update
            documents: Optional new document texts
            metadatas: Optional new metadata dictionaries
        """
        self.collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Updated {len(ids)} documents in collection {self.collection_name}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.
        
        Returns:
            Collection information including count and metadata
        """
        count = self.collection.count()
        return {
            "name": self.collection_name,
            "count": count,
            "embedding_function": str(self.embedding_function),
        }
    
    def list_collections(self) -> List[str]:
        """
        List all available collections.
        
        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def create_collection(self, name: str, embedding_function: Optional[Any] = None) -> None:
        """
        Create a new collection.
        
        Args:
            name: Name of the new collection
            embedding_function: Optional custom embedding function
        """
        ef = embedding_function or self.embedding_function
        self.client.create_collection(name=name, embedding_function=ef)
        logger.info(f"Created new collection: {name}")
    
    def switch_collection(self, name: str) -> None:
        """
        Switch to a different collection.
        
        Args:
            name: Name of the collection to switch to
        """
        self.collection = self.client.get_collection(name=name)
        self.collection_name = name
        logger.info(f"Switched to collection: {name}")
    
    def reset_collection(self) -> None:
        """Reset the current collection by deleting all documents."""
        # Get all document IDs
        all_docs = self.collection.get()
        if all_docs["ids"]:
            self.collection.delete(ids=all_docs["ids"])
            logger.info(f"Reset collection {self.collection_name} - deleted all documents")
        else:
            logger.info(f"Collection {self.collection_name} is already empty")