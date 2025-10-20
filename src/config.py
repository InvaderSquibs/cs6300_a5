"""
Configuration settings for the vector database template.
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "chromadb": {
        "collection_name": "default_collection",
        "persist_directory": "./data/vector_db"
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
    },
    "llm": {
        "provider": "lmstudio",
        "model": "qwen/qwen3-4b-2507",
        "base_url": "http://localhost:1234",
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "rag": {
        "top_k": 5,
        "context_window": 3,
        "cache_ttl": 300,
        "max_cache_size": 50
    },
    "arxiv": {
        "max_papers": 12,
        "pause_sec": 3.0,
        "sort_by": "submittedDate",
        "sort_order": "descending"
    },
    "chat_history": {
        "save_dir": "./data/chat_history",
        "auto_save": True
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
    
    # LLM settings
    if os.getenv("LLM_MODEL"):
        config["llm"]["model"] = os.getenv("LLM_MODEL")
    
    if os.getenv("LLM_BASE_URL"):
        config["llm"]["base_url"] = os.getenv("LLM_BASE_URL")
    
    # RAG settings
    if os.getenv("RAG_TOP_K"):
        config["rag"]["top_k"] = int(os.getenv("RAG_TOP_K"))
    
    # ArXiv settings
    if os.getenv("ARXIV_MAX_PAPERS"):
        config["arxiv"]["max_papers"] = int(os.getenv("ARXIV_MAX_PAPERS"))
    
    # Chat history settings
    if os.getenv("CHAT_HISTORY_DIR"):
        config["chat_history"]["save_dir"] = os.getenv("CHAT_HISTORY_DIR")
    
    return config