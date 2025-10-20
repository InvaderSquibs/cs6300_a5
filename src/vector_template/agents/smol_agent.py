"""Smolagents integration for vector database operations."""

from typing import Any, Dict, List, Optional, Union
from smolagents import CodeAgent, tool
import logging
from ..database.chroma_client import ChromaVectorDB

logger = logging.getLogger(__name__)


class SmolVectorAgent:
    """
    A smolagents-based agent that can interact with vector databases.
    
    This agent provides tools for managing and querying vector databases
    through the smolagents framework.
    """
    
    def __init__(
        self,
        vector_db: Optional[ChromaVectorDB] = None,
        persist_directory: str = "./chroma_db",
        collection_name: str = "smol_agent_collection",
    ):
        """
        Initialize the SmolVectorAgent.
        
        Args:
            vector_db: Existing ChromaVectorDB instance (optional)
            persist_directory: Directory for database persistence
            collection_name: Name of the collection to use
        """
        if vector_db is None:
            self.vector_db = ChromaVectorDB(
                persist_directory=persist_directory,
                collection_name=collection_name
            )
        else:
            self.vector_db = vector_db
        
        # Initialize the agent with vector tools
        self.agent = CodeAgent(tools=[
            self.add_document_tool,
            self.search_documents_tool,
            self.delete_document_tool,
            self.get_collection_info_tool,
            self.list_collections_tool,
        ])
        
        logger.info(f"Initialized SmolVectorAgent with collection: {collection_name}")
    
    @tool
    def add_document_tool(
        self,
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> str:
        """
        Add a document to the vector database.
        
        Args:
            document: The document text to add
            metadata: Optional metadata for the document
            doc_id: Optional ID for the document
            
        Returns:
            Success message
        """
        try:
            documents = [document]
            metadatas = [metadata] if metadata else None
            ids = [doc_id] if doc_id else None
            
            self.vector_db.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return f"Successfully added document to vector database"
        except Exception as e:
            error_msg = f"Error adding document: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @tool
    def search_documents_tool(
        self,
        query: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Search for similar documents in the vector database.
        
        Args:
            query: The search query
            n_results: Number of results to return
            metadata_filter: Optional metadata filter
            
        Returns:
            Formatted search results
        """
        try:
            results = self.vector_db.query(
                query_texts=query,
                n_results=n_results,
                where=metadata_filter
            )
            
            if not results["documents"] or not results["documents"][0]:
                return "No documents found matching the query."
            
            # Format results
            formatted_results = []
            documents = results["documents"][0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]
            
            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else "N/A"
                doc_id = ids[i] if i < len(ids) else "N/A"
                
                formatted_results.append(
                    f"Document {i+1} (ID: {doc_id}, Distance: {distance:.4f}):\n"
                    f"Content: {doc[:200]}{'...' if len(doc) > 200 else ''}\n"
                    f"Metadata: {metadata}\n"
                )
            
            return "\\n".join(formatted_results)
        
        except Exception as e:
            error_msg = f"Error searching documents: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @tool
    def delete_document_tool(self, doc_id: str) -> str:
        """
        Delete a document from the vector database.
        
        Args:
            doc_id: ID of the document to delete
            
        Returns:
            Success or error message
        """
        try:
            self.vector_db.delete_documents([doc_id])
            return f"Successfully deleted document with ID: {doc_id}"
        except Exception as e:
            error_msg = f"Error deleting document: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @tool
    def get_collection_info_tool(self) -> str:
        """
        Get information about the current collection.
        
        Returns:
            Collection information as a formatted string
        """
        try:
            info = self.vector_db.get_collection_info()
            return (
                f"Collection Information:\\n"
                f"Name: {info['name']}\\n"
                f"Document Count: {info['count']}\\n"
                f"Embedding Function: {info['embedding_function']}"
            )
        except Exception as e:
            error_msg = f"Error getting collection info: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @tool
    def list_collections_tool(self) -> str:
        """
        List all available collections.
        
        Returns:
            List of collection names as a formatted string
        """
        try:
            collections = self.vector_db.list_collections()
            if collections:
                return f"Available collections: {', '.join(collections)}"
            else:
                return "No collections found."
        except Exception as e:
            error_msg = f"Error listing collections: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def run(self, task: str) -> str:
        """
        Run a task using the agent.
        
        Args:
            task: The task description for the agent
            
        Returns:
            The agent's response
        """
        try:
            return self.agent.run(task)
        except Exception as e:
            error_msg = f"Error running agent task: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def add_recipe_documents(self, recipes: List[Dict[str, Any]]) -> str:
        """
        Specialized method for adding recipe documents.
        
        Args:
            recipes: List of recipe dictionaries with fields like name, ingredients, instructions
            
        Returns:
            Success message with count of added recipes
        """
        try:
            documents = []
            metadatas = []
            ids = []
            
            for i, recipe in enumerate(recipes):
                # Create document text from recipe
                doc_text = f"Recipe: {recipe.get('name', 'Unknown')}\\n"
                if 'ingredients' in recipe:
                    doc_text += f"Ingredients: {', '.join(recipe['ingredients'])}\\n"
                if 'instructions' in recipe:
                    doc_text += f"Instructions: {recipe['instructions']}\\n"
                if 'description' in recipe:
                    doc_text += f"Description: {recipe['description']}"
                
                documents.append(doc_text)
                
                # Create metadata
                metadata = {
                    "type": "recipe",
                    "name": recipe.get('name', 'Unknown'),
                    "cuisine": recipe.get('cuisine', 'Unknown'),
                    "prep_time": recipe.get('prep_time'),
                    "cook_time": recipe.get('cook_time'),
                    "servings": recipe.get('servings'),
                }
                metadatas.append(metadata)
                
                # Create ID
                recipe_id = recipe.get('id', f"recipe_{i}")
                ids.append(recipe_id)
            
            self.vector_db.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return f"Successfully added {len(recipes)} recipes to the vector database"
        
        except Exception as e:
            error_msg = f"Error adding recipes: {str(e)}"
            logger.error(error_msg)
            return error_msg