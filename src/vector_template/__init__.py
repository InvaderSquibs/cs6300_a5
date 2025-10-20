"""Vector Template - A template for vector databases with smolagents integration."""

__version__ = "0.1.0"
__author__ = "Vector Template Team"

# Optional imports - only available if dependencies are installed
try:
    from .database.chroma_client import ChromaVectorDB
    _CHROMA_AVAILABLE = True
except ImportError:
    ChromaVectorDB = None
    _CHROMA_AVAILABLE = False

try:
    from .agents.smol_agent import SmolVectorAgent
    _SMOL_AGENT_AVAILABLE = True
except ImportError:
    SmolVectorAgent = None
    _SMOL_AGENT_AVAILABLE = False

try:
    from .api.server import create_app
    _API_AVAILABLE = True
except ImportError:
    create_app = None
    _API_AVAILABLE = False

__all__ = ["ChromaVectorDB", "SmolVectorAgent", "create_app"]