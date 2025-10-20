"""FastAPI server for vector database operations."""

from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
from ..database.chroma_client import ChromaVectorDB
from ..agents.smol_agent import SmolVectorAgent

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class DocumentRequest(BaseModel):
    """Request model for adding documents."""
    documents: List[str] = Field(..., description="List of document texts")
    metadatas: Optional[List[Dict[str, Any]]] = Field(None, description="Optional metadata for each document")
    ids: Optional[List[str]] = Field(None, description="Optional IDs for each document")


class QueryRequest(BaseModel):
    """Request model for querying documents."""
    query_texts: Union[str, List[str]] = Field(..., description="Query text(s)")
    n_results: int = Field(10, description="Number of results to return", ge=1, le=100)
    where: Optional[Dict[str, Any]] = Field(None, description="Metadata filter")
    include: Optional[List[str]] = Field(["documents", "metadatas", "distances"], description="What to include in results")


class DeleteRequest(BaseModel):
    """Request model for deleting documents."""
    ids: List[str] = Field(..., description="List of document IDs to delete")


class UpdateRequest(BaseModel):
    """Request model for updating documents."""
    ids: List[str] = Field(..., description="List of document IDs to update")
    documents: Optional[List[str]] = Field(None, description="New document texts")
    metadatas: Optional[List[Dict[str, Any]]] = Field(None, description="New metadata")


class AgentTaskRequest(BaseModel):
    """Request model for agent tasks."""
    task: str = Field(..., description="Task description for the agent")


class RecipeRequest(BaseModel):
    """Request model for adding recipes."""
    recipes: List[Dict[str, Any]] = Field(..., description="List of recipe dictionaries")


class CollectionRequest(BaseModel):
    """Request model for collection operations."""
    name: str = Field(..., description="Collection name")


# Global variables to hold database and agent instances
vector_db: Optional[ChromaVectorDB] = None
smol_agent: Optional[SmolVectorAgent] = None


def get_vector_db() -> ChromaVectorDB:
    """Dependency to get the vector database instance."""
    global vector_db
    if vector_db is None:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    return vector_db


def get_smol_agent() -> SmolVectorAgent:
    """Dependency to get the smol agent instance."""
    global smol_agent
    if smol_agent is None:
        raise HTTPException(status_code=500, detail="Smol agent not initialized")
    return smol_agent


def create_app(
    persist_directory: str = "./chroma_db",
    collection_name: str = "api_collection",
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        persist_directory: Directory for database persistence
        collection_name: Default collection name
        host: Chroma server host (for client-server mode)
        port: Chroma server port (for client-server mode)
        
    Returns:
        Configured FastAPI application
    """
    global vector_db, smol_agent
    
    # Initialize vector database
    vector_db = ChromaVectorDB(
        persist_directory=persist_directory,
        collection_name=collection_name,
        host=host,
        port=port,
    )
    
    # Initialize smol agent
    smol_agent = SmolVectorAgent(vector_db=vector_db)
    
    # Create FastAPI app
    app = FastAPI(
        title="Vector Template API",
        description="API for vector database operations with smolagents integration",
        version="0.1.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "Vector Template API", "version": "0.1.0"}
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            db = get_vector_db()
            info = db.get_collection_info()
            return {"status": "healthy", "collection_info": info}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
    
    # Document management endpoints
    @app.post("/documents/add")
    async def add_documents(
        request: DocumentRequest,
        db: ChromaVectorDB = Depends(get_vector_db)
    ):
        """Add documents to the vector database."""
        try:
            db.add_documents(
                documents=request.documents,
                metadatas=request.metadatas,
                ids=request.ids
            )
            return {"message": f"Successfully added {len(request.documents)} documents"}
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/documents/query")
    async def query_documents(
        request: QueryRequest,
        db: ChromaVectorDB = Depends(get_vector_db)
    ):
        """Query documents in the vector database."""
        try:
            results = db.query(
                query_texts=request.query_texts,
                n_results=request.n_results,
                where=request.where,
                include=request.include
            )
            return {"results": results}
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/documents/delete")
    async def delete_documents(
        request: DeleteRequest,
        db: ChromaVectorDB = Depends(get_vector_db)
    ):
        """Delete documents from the vector database."""
        try:
            db.delete_documents(request.ids)
            return {"message": f"Successfully deleted {len(request.ids)} documents"}
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/documents/update")
    async def update_documents(
        request: UpdateRequest,
        db: ChromaVectorDB = Depends(get_vector_db)
    ):
        """Update documents in the vector database."""
        try:
            db.update_documents(
                ids=request.ids,
                documents=request.documents,
                metadatas=request.metadatas
            )
            return {"message": f"Successfully updated {len(request.ids)} documents"}
        except Exception as e:
            logger.error(f"Error updating documents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Collection management endpoints
    @app.get("/collections/info")
    async def get_collection_info(db: ChromaVectorDB = Depends(get_vector_db)):
        """Get information about the current collection."""
        try:
            info = db.get_collection_info()
            return {"collection_info": info}
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/collections/list")
    async def list_collections(db: ChromaVectorDB = Depends(get_vector_db)):
        """List all available collections."""
        try:
            collections = db.list_collections()
            return {"collections": collections}
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/collections/create")
    async def create_collection(
        request: CollectionRequest,
        db: ChromaVectorDB = Depends(get_vector_db)
    ):
        """Create a new collection."""
        try:
            db.create_collection(request.name)
            return {"message": f"Successfully created collection: {request.name}"}
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/collections/switch")
    async def switch_collection(
        request: CollectionRequest,
        db: ChromaVectorDB = Depends(get_vector_db)
    ):
        """Switch to a different collection."""
        try:
            db.switch_collection(request.name)
            return {"message": f"Successfully switched to collection: {request.name}"}
        except Exception as e:
            logger.error(f"Error switching collection: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/collections/reset")
    async def reset_collection(db: ChromaVectorDB = Depends(get_vector_db)):
        """Reset the current collection by deleting all documents."""
        try:
            db.reset_collection()
            return {"message": "Successfully reset collection"}
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Agent endpoints
    @app.post("/agent/task")
    async def run_agent_task(
        request: AgentTaskRequest,
        agent: SmolVectorAgent = Depends(get_smol_agent)
    ):
        """Run a task using the smol agent."""
        try:
            result = agent.run(request.task)
            return {"result": result}
        except Exception as e:
            logger.error(f"Error running agent task: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Specialized endpoints for recipes
    @app.post("/recipes/add")
    async def add_recipes(
        request: RecipeRequest,
        agent: SmolVectorAgent = Depends(get_smol_agent)
    ):
        """Add recipes to the vector database using the specialized method."""
        try:
            result = agent.add_recipe_documents(request.recipes)
            return {"message": result}
        except Exception as e:
            logger.error(f"Error adding recipes: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


# Create a default app instance
app = create_app()