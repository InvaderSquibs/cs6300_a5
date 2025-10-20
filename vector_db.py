"""
Vector database manager using ChromaDB for local storage
"""

import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Optional
import os

class VectorDBManager:
    """Manager for vector database operations using ChromaDB"""
    
    def __init__(self, db_path: str = "./chroma_db"):
        """
        Initialize the vector database manager
        
        Args:
            db_path: Path to store the ChromaDB database
        """
        self.db_path = db_path
        
        # Create the database directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get the collection for recipe summaries
        self.collection_name = "recipe_summaries"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection '{self.collection_name}'")
        except ValueError:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Recipe summaries for vector search"}
            )
            print(f"Created new collection '{self.collection_name}'")
    
    def add_recipe_summary(self, recipe_name: str, summary: str, metadata: Optional[Dict] = None) -> str:
        """
        Add a recipe summary to the vector database
        
        Args:
            recipe_name: Name of the recipe
            summary: LLM-generated summary of the recipe
            metadata: Optional metadata about the recipe
            
        Returns:
            Document ID of the added summary
        """
        # Generate a unique ID for this document
        doc_id = str(uuid.uuid4())
        
        # Prepare metadata
        doc_metadata = {
            "recipe_name": recipe_name,
            "type": "recipe_summary"
        }
        if metadata:
            doc_metadata.update(metadata)
        
        # Add to the collection
        self.collection.add(
            documents=[summary],
            metadatas=[doc_metadata],
            ids=[doc_id]
        )
        
        print(f"Added recipe summary for '{recipe_name}' with ID: {doc_id}")
        return doc_id
    
    def query_recipes(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector database for similar recipe summaries
        
        Args:
            query: Query string to search for
            n_results: Number of results to return
            
        Returns:
            List of matching results with metadata and distances
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format the results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                docs = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                ids = results['ids'][0]
                
                for i, doc in enumerate(docs):
                    formatted_results.append({
                        "id": ids[i],
                        "document": doc,
                        "metadata": metadatas[i],
                        "distance": distances[i],
                        "similarity_score": 1 - distances[i]  # Convert distance to similarity
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error querying vector database: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the current collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "db_path": self.db_path
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "db_path": self.db_path,
                "error": str(e)
            }
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            # Get all document IDs
            all_docs = self.collection.get()
            if all_docs['ids']:
                # Delete all documents
                self.collection.delete(ids=all_docs['ids'])
                print(f"Cleared {len(all_docs['ids'])} documents from collection")
            else:
                print("Collection is already empty")
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def reset_database(self):
        """Reset the entire database (use with caution!)"""
        try:
            self.client.reset()
            print("Database reset successfully")
            # Recreate the collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Recipe summaries for vector search"}
            )
        except Exception as e:
            print(f"Error resetting database: {e}")
    
    def list_all_recipes(self) -> List[Dict[str, Any]]:
        """List all recipes in the database"""
        try:
            all_docs = self.collection.get(include=["documents", "metadatas"])
            
            recipes = []
            if all_docs['documents']:
                for i, doc in enumerate(all_docs['documents']):
                    recipes.append({
                        "id": all_docs['ids'][i],
                        "recipe_name": all_docs['metadatas'][i].get('recipe_name', 'Unknown'),
                        "summary": doc[:100] + "..." if len(doc) > 100 else doc
                    })
            
            return recipes
            
        except Exception as e:
            print(f"Error listing recipes: {e}")
            return []