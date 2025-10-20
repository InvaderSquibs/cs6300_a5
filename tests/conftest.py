"""Test configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vector_template.database.chroma_client import ChromaVectorDB
from vector_template.agents.smol_agent import SmolVectorAgent


@pytest.fixture
def temp_db_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def vector_db(temp_db_dir):
    """Create a test vector database instance."""
    return ChromaVectorDB(
        persist_directory=temp_db_dir,
        collection_name="test_collection"
    )


@pytest.fixture
def smol_agent(vector_db):
    """Create a test smol agent instance."""
    return SmolVectorAgent(vector_db=vector_db)


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        "This is a test document about cooking pasta.",
        "A recipe for chocolate cake with rich flavors.",
        "How to make a perfect chicken curry with spices.",
    ]


@pytest.fixture
def sample_recipes():
    """Sample recipe data for testing."""
    return [
        {
            "id": "recipe_1",
            "name": "Test Pasta",
            "ingredients": ["pasta", "tomatoes", "cheese"],
            "instructions": "Cook pasta, add sauce, serve.",
            "prep_time": "10 minutes",
            "cuisine": "Italian"
        },
        {
            "id": "recipe_2",
            "name": "Test Cake",
            "ingredients": ["flour", "sugar", "chocolate"],
            "instructions": "Mix ingredients, bake for 30 minutes.",
            "prep_time": "15 minutes",
            "cuisine": "International"
        }
    ]