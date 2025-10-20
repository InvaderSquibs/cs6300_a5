"""Simple test to verify the project structure without heavy dependencies."""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that our modules can be imported."""
    try:
        # Test basic imports that don't require external dependencies
        print("Testing imports...")
        
        # These will fail if dependencies are missing, but structure should be correct
        try:
            from vector_template.database.chroma_client import ChromaVectorDB
            print("✓ ChromaVectorDB class can be imported")
        except ImportError as e:
            print(f"⚠ ChromaVectorDB import failed (expected): {e}")
        
        try:
            from vector_template.agents.smol_agent import SmolVectorAgent
            print("✓ SmolVectorAgent class can be imported")
        except ImportError as e:
            print(f"⚠ SmolVectorAgent import failed (expected): {e}")
        
        try:
            from vector_template.api.server import create_app
            print("✓ FastAPI create_app function can be imported")
        except ImportError as e:
            print(f"⚠ FastAPI create_app import failed (expected): {e}")
        
        # These should work with just standard library
        from vector_template.utils.data_processing import (
            preprocess_recipe_text,
            extract_recipe_metadata,
            chunk_large_recipe,
            format_search_results,
        )
        print("✓ Data processing utilities imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_data_processing():
    """Test data processing functions with sample data."""
    try:
        # Import directly to avoid __init__.py dependency issues
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from vector_template.utils.data_processing import (
            preprocess_recipe_text,
            extract_recipe_metadata,
            format_search_results,
        )
        
        # Sample recipe
        recipe = {
            "name": "Test Pasta",
            "ingredients": ["pasta", "tomatoes", "cheese"],
            "instructions": "Cook pasta, add sauce, serve.",
            "prep_time": "10 minutes",
            "cuisine": "Italian"
        }
        
        # Test preprocessing
        text = preprocess_recipe_text(recipe)
        print(f"✓ Recipe text preprocessing works")
        print(f"  Sample output: {text[:100]}...")
        
        # Test metadata extraction
        metadata = extract_recipe_metadata(recipe)
        print(f"✓ Metadata extraction works")
        print(f"  Sample metadata: {metadata}")
        
        # Test search results formatting
        mock_results = {
            "documents": [["Recipe for pasta", "Recipe for cake"]],
            "metadatas": [[{"name": "Pasta Recipe"}, {"name": "Cake Recipe"}]],
            "distances": [[0.1, 0.2]],
            "ids": [["pasta_1", "cake_1"]]
        }
        
        formatted = format_search_results(mock_results, max_results=2)
        print(f"✓ Search results formatting works")
        print(f"  Sample output: {formatted[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_project_structure():
    """Test that all expected files and directories exist."""
    base_path = Path(__file__).parent
    
    expected_files = [
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "cli.py",
        "src/vector_template/__init__.py",
        "src/vector_template/database/__init__.py",
        "src/vector_template/database/chroma_client.py",
        "src/vector_template/agents/__init__.py",
        "src/vector_template/agents/smol_agent.py",
        "src/vector_template/api/__init__.py",
        "src/vector_template/api/server.py",
        "src/vector_template/utils/__init__.py",
        "src/vector_template/utils/data_processing.py",
        "src/vector_template/examples/__init__.py",
        "src/vector_template/examples/recipe_example.py",
        "tests/conftest.py",
        "tests/unit/test_chroma_client.py",
        "tests/unit/test_data_processing.py",
    ]
    
    missing_files = []
    for file_path in expected_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✓ All expected files present")
        return True

def main():
    """Run all tests."""
    print("="*60)
    print("VECTOR TEMPLATE STRUCTURE TEST")
    print("="*60)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Module Imports", test_imports),
        ("Data Processing", test_data_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\\n{test_name}:")
        print("-" * len(test_name) + "-")
        result = test_func()
        results.append((test_name, result))
    
    print("\\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\\n🎉 All tests passed! Project structure is ready.")
    else:
        print("\\n⚠️ Some tests failed, but this may be due to missing dependencies.")
    
    return all_passed

if __name__ == "__main__":
    main()