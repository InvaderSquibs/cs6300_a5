"""
FastAPI Server for Vector Database Template

This module provides a REST API server for interacting with vector databases.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
from src.vector_db_populator import VectorDBPopulator, create_sample_data

app = FastAPI(
    title="Vector Database Template API",
    description="API for populating and searching vector databases",
    version="1.0.0"
)

# Global populator instance
populator: Optional[VectorDBPopulator] = None


class PopulateRequest(BaseModel):
    """Request model for populating the database with texts."""
    texts: List[str]
    metadata: Optional[List[Dict[str, Any]]] = None
    backend_type: Optional[str] = "chromadb"
    collection_name: Optional[str] = "default_collection"


class SearchRequest(BaseModel):
    """Request model for searching similar vectors."""
    query: str
    top_k: Optional[int] = 10


class InitializeRequest(BaseModel):
    """Request model for initializing the vector database."""
    backend_type: Optional[str] = "chromadb"
    collection_name: Optional[str] = "default_collection"
    encoder_model: Optional[str] = "all-MiniLM-L6-v2"


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Vector Database Template API",
        "version": "1.0.0",
        "endpoints": {
            "initialize": "POST /initialize - Initialize the vector database",
            "populate": "POST /populate - Populate with texts",
            "populate_sample": "POST /populate/sample - Populate with sample data",
            "search": "POST /search - Search for similar vectors",
            "health": "GET /health - Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "populator_initialized": populator is not None
    }


@app.post("/initialize")
async def initialize_database(request: InitializeRequest):
    """Initialize the vector database with specified configuration."""
    global populator
    
    try:
        populator = VectorDBPopulator(backend_type=request.backend_type)
        populator.initialize_encoder(request.encoder_model)
        populator.initialize_database({
            'collection_name': request.collection_name
        })
        
        return {
            "message": "Vector database initialized successfully",
            "backend_type": request.backend_type,
            "collection_name": request.collection_name,
            "encoder_model": request.encoder_model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")


@app.post("/populate")
async def populate_database(request: PopulateRequest):
    """Populate the vector database with provided texts."""
    global populator
    
    if populator is None:
        # Auto-initialize with default settings
        populator = VectorDBPopulator(backend_type=request.backend_type)
        populator.initialize_encoder()
        populator.initialize_database({
            'collection_name': request.collection_name
        })
    
    try:
        populator.populate_from_texts(request.texts, request.metadata)
        
        return {
            "message": f"Successfully populated database with {len(request.texts)} texts",
            "count": len(request.texts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to populate database: {str(e)}")


@app.post("/populate/sample")
async def populate_with_sample_data():
    """Populate the vector database with sample data."""
    global populator
    
    if populator is None:
        # Auto-initialize with default settings
        populator = VectorDBPopulator(backend_type='chromadb')
        populator.initialize_encoder()
        populator.initialize_database({'collection_name': 'sample_collection'})
    
    try:
        texts, metadata = create_sample_data()
        populator.populate_from_texts(texts, metadata)
        
        return {
            "message": f"Successfully populated database with {len(texts)} sample texts",
            "count": len(texts),
            "sample_categories": list(set(m["category"] for m in metadata))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to populate with sample data: {str(e)}")


@app.post("/search")
async def search_similar(request: SearchRequest):
    """Search for similar vectors in the database."""
    global populator
    
    if populator is None:
        raise HTTPException(
            status_code=400, 
            detail="Vector database not initialized. Call /initialize or /populate first."
        )
    
    try:
        results = populator.search_similar(request.query, request.top_k)
        
        return {
            "query": request.query,
            "top_k": request.top_k,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/status")
async def get_status():
    """Get the current status of the vector database."""
    global populator
    
    if populator is None:
        return {
            "initialized": False,
            "backend_type": None,
            "encoder_loaded": False
        }
    
    return {
        "initialized": True,
        "backend_type": populator.backend_type,
        "encoder_loaded": populator.encoder is not None
    }


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the FastAPI server."""
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    start_server(reload=True)