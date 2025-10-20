"""
Configuration settings for the vector database template.
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "chromadb": {
        "collection_name": "default_collection",
        "persist_directory": "./chroma_db"
    },
    "faiss": {
        "dimension": 384,
        "index_file": "./faiss_index.index",
        "metadata_file": "./faiss_metadata.json"
    },
    "encoder": {
        "model_name": "all-MiniLM-L6-v2",
        "cache_folder": "./model_cache"
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": False
    }
}


def get_config() -> Dict[str, Any]:
    """Get configuration settings with environment variable overrides."""
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables if present
    if os.getenv("CHROMADB_COLLECTION"):
        config["chromadb"]["collection_name"] = os.getenv("CHROMADB_COLLECTION")
    
    if os.getenv("CHROMADB_PERSIST_DIR"):
        config["chromadb"]["persist_directory"] = os.getenv("CHROMADB_PERSIST_DIR")
    
    if os.getenv("FAISS_DIMENSION"):
        config["faiss"]["dimension"] = int(os.getenv("FAISS_DIMENSION"))
    
    if os.getenv("ENCODER_MODEL"):
        config["encoder"]["model_name"] = os.getenv("ENCODER_MODEL")
    
    if os.getenv("SERVER_HOST"):
        config["server"]["host"] = os.getenv("SERVER_HOST")
    
    if os.getenv("SERVER_PORT"):
        config["server"]["port"] = int(os.getenv("SERVER_PORT"))
    
    return config