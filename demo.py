#!/usr/bin/env python3
"""
Demo script for the Vector Template project.

This script demonstrates the core functionality without requiring heavy dependencies.
When dependencies are installed, it will provide full functionality.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_dependencies():
    """Check which dependencies are available."""
    dependencies = {
        'chromadb': False,
        'smolagents': False,
        'fastapi': False,
        'pandas': False,
        'sentence-transformers': False,
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies

def demo_data_processing():
    """Demonstrate data processing capabilities."""
    print("\\n" + "="*60)
    print("DATA PROCESSING DEMO")
    print("="*60)
    
    from vector_template.utils.data_processing import (
        preprocess_recipe_text,
        extract_recipe_metadata,
        chunk_large_recipe,
        format_search_results,
    )
    
    # Sample recipes
    recipes = [
        {
            "id": "pasta_carbonara",
            "name": "Classic Pasta Carbonara",
            "description": "A traditional Italian pasta dish with eggs, cheese, and pancetta",
            "ingredients": [
                "400g spaghetti",
                "200g pancetta",
                "4 large eggs",
                "100g Pecorino Romano cheese",
                "Black pepper",
                "Salt"
            ],
            "instructions": "1. Cook pasta in salted water. 2. Fry pancetta until crispy. 3. Mix eggs and cheese. 4. Combine hot pasta with pancetta, then add egg mixture off heat. 5. Toss quickly and serve.",
            "prep_time": "10 minutes",
            "cook_time": "15 minutes",
            "servings": 4,
            "cuisine": "Italian"
        },
        {
            "id": "chicken_curry",
            "name": "Spicy Chicken Curry",
            "description": "A flavorful and aromatic chicken curry with Indian spices",
            "ingredients": [
                "500g chicken breast",
                "2 onions",
                "3 cloves garlic",
                "1 inch ginger",
                "2 tsp curry powder",
                "1 tsp turmeric",
                "400ml coconut milk"
            ],
            "instructions": "1. Cut chicken into pieces. 2. Sauté onions, garlic, and ginger. 3. Add spices and cook for 1 minute. 4. Add chicken and brown. 5. Pour in coconut milk and simmer for 20 minutes.",
            "prep_time": "15 minutes",
            "cook_time": "25 minutes",
            "servings": 4,
            "cuisine": "Indian"
        }
    ]
    
    print("\\n1. Recipe Text Preprocessing:")
    print("-" * 30)
    for recipe in recipes:
        text = preprocess_recipe_text(recipe)
        print(f"\\n{recipe['name']}:")
        print(text[:200] + "..." if len(text) > 200 else text)
    
    print("\\n2. Metadata Extraction:")
    print("-" * 25)
    for recipe in recipes:
        metadata = extract_recipe_metadata(recipe)
        print(f"\\n{recipe['name']}: {metadata}")
    
    print("\\n3. Recipe Chunking (for large recipes):")
    print("-" * 40)
    # Create a large recipe for chunking demo
    large_recipe = recipes[0].copy()
    large_recipe["instructions"] = large_recipe["instructions"] * 10  # Make it very long
    
    chunks = chunk_large_recipe(large_recipe, max_chunk_size=300)
    print(f"Original recipe split into {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {chunk['metadata']['chunk_type']} ({len(chunk['text'])} chars)")
    
    print("\\n4. Search Results Formatting:")
    print("-" * 32)
    # Mock search results
    mock_results = {
        "documents": [
            [preprocess_recipe_text(recipes[0]), preprocess_recipe_text(recipes[1])]
        ],
        "metadatas": [
            [extract_recipe_metadata(recipes[0]), extract_recipe_metadata(recipes[1])]
        ],
        "distances": [[0.1, 0.3]],
        "ids": [["pasta_carbonara", "chicken_curry"]]
    }
    
    formatted = format_search_results(mock_results)
    print(formatted)

def demo_vector_database():
    """Demonstrate vector database functionality (if available)."""
    print("\\n" + "="*60)
    print("VECTOR DATABASE DEMO")
    print("="*60)
    
    try:
        from vector_template.database.chroma_client import ChromaVectorDB
        
        print("✓ ChromaDB client available - would demonstrate:")
        print("  - Database initialization")
        print("  - Document addition and querying")
        print("  - Collection management")
        print("  - Metadata filtering")
        
        # Would create database and add sample data here
        print("\\n[Full demo available when ChromaDB is installed]")
        
    except ImportError:
        print("❌ ChromaDB not available")
        print("   Install with: pip install chromadb>=0.4.0")
        print("\\n   Would demonstrate:")
        print("   - Vector similarity search")
        print("   - Document embedding and storage")
        print("   - Collection operations")

def demo_smolagents():
    """Demonstrate smolagents functionality (if available)."""
    print("\\n" + "="*60)
    print("SMOLAGENTS DEMO")
    print("="*60)
    
    try:
        from vector_template.agents.smol_agent import SmolVectorAgent
        
        print("✓ SmolVectorAgent available - would demonstrate:")
        print("  - AI agent initialization")
        print("  - Natural language queries")
        print("  - Automated recipe processing")
        print("  - Intelligent search operations")
        
        print("\\n[Full demo available when smolagents and ChromaDB are installed]")
        
    except ImportError:
        print("❌ SmolVectorAgent not available")
        print("   Install with: pip install smolagents>=0.1.0 chromadb>=0.4.0")
        print("\\n   Would demonstrate:")
        print("   - 'Find me Italian pasta recipes'")
        print("   - 'Add this recipe to the database'")
        print("   - 'Search for quick dinner ideas'")

def demo_api_server():
    """Demonstrate API server functionality (if available)."""
    print("\\n" + "="*60)
    print("API SERVER DEMO")
    print("="*60)
    
    try:
        from vector_template.api.server import create_app
        
        print("✓ FastAPI server available - would demonstrate:")
        print("  - RESTful API endpoints")
        print("  - Document CRUD operations")
        print("  - Collection management")
        print("  - Agent task execution")
        
        print("\\n   Available endpoints:")
        endpoints = [
            "POST /documents/add",
            "POST /documents/query", 
            "DELETE /documents/delete",
            "GET /collections/info",
            "POST /agent/task",
            "POST /recipes/add"
        ]
        for endpoint in endpoints:
            print(f"   - {endpoint}")
        
        print("\\n[Start server with: python cli.py serve]")
        
    except ImportError:
        print("❌ FastAPI server not available")
        print("   Install with: pip install fastapi uvicorn")
        print("\\n   Would provide:")
        print("   - REST API for vector operations")
        print("   - Web-based recipe management")
        print("   - Integration with external services")

def main():
    """Run the demo."""
    print("="*80)
    print("VECTOR TEMPLATE COMPREHENSIVE DEMO")
    print("="*80)
    
    # Check dependencies
    deps = check_dependencies()
    print("\\nDependency Status:")
    print("-" * 18)
    for dep, available in deps.items():
        status = "✓ Available" if available else "❌ Missing"
        print(f"  {dep:<20} {status}")
    
    if not any(deps.values()):
        print("\\n⚠️  No optional dependencies installed.")
        print("   Install them with: pip install -r requirements.txt")
    
    # Always demonstrate data processing (no external deps required)
    demo_data_processing()
    
    # Demonstrate other features based on availability
    demo_vector_database()
    demo_smolagents()
    demo_api_server()
    
    print("\\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\\n1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\\n2. Try the CLI:")
    print("   python cli.py example")
    print("   python cli.py serve")
    print("   python cli.py interactive")
    print("\\n3. Load your own recipe data:")
    print("   python cli.py example --csv-file your_recipes.csv")
    print("\\n4. Use in your own projects:")
    print("   from vector_template import ChromaVectorDB, SmolVectorAgent")
    print("\\n5. Access the API documentation:")
    print("   Visit http://localhost:8000/docs after starting the server")
    
    print("\\n🚀 Ready to build amazing vector database applications!")

if __name__ == "__main__":
    main()