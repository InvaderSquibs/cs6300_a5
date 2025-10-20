#!/usr/bin/env python3
"""
Vector Database Validation Script

This script validates a local vector database by:
1. Connecting to a local LLM via the GPT_API environment variable
2. Generating summaries of random recipes
3. Storing summaries in a local vector database
4. Querying the database to test retrieval functionality

Usage:
    python validate_vdb.py [options]

Environment Variables:
    GPT_API: URL endpoint for local LLM API (required)
    API_KEY: API key if required by your LLM setup (optional)
    MODEL_NAME: Name of the model to use (optional, defaults to 'llama2')
"""

import argparse
import os
import sys
import time
from typing import List, Dict, Any

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recipe_data import get_random_recipe, format_recipe_for_summary, SAMPLE_RECIPES
from llm_client import LocalLLMClient
from vector_db import VectorDBManager

def print_banner():
    """Print a nice banner for the script"""
    print("=" * 60)
    print("  VECTOR DATABASE VALIDATION SCRIPT")
    print("=" * 60)
    print()

def validate_environment():
    """Validate that required environment variables are set"""
    print("🔍 Validating environment configuration...")
    
    gpt_api = os.getenv('GPT_API')
    if not gpt_api:
        print("❌ ERROR: GPT_API environment variable not set!")
        print("   Please set GPT_API to your local LLM endpoint URL")
        print("   Example: export GPT_API='http://localhost:11434/v1/chat/completions'")
        return False
    
    print(f"✅ GPT_API: {gpt_api}")
    
    model_name = os.getenv('MODEL_NAME', 'llama2')
    print(f"✅ Model: {model_name}")
    
    api_key = os.getenv('API_KEY')
    if api_key:
        print(f"✅ API Key: {'*' * len(api_key[:4])}...")
    else:
        print("ℹ️  No API key configured (may not be needed)")
    
    print()
    return True

def test_llm_connection(llm_client: LocalLLMClient) -> bool:
    """Test connection to the local LLM"""
    print("🔗 Testing LLM connection...")
    
    if llm_client.test_connection():
        print("✅ LLM connection successful!")
        return True
    else:
        print("❌ LLM connection failed!")
        print("   Please ensure your local LLM is running and accessible")
        return False

def initialize_vector_db(db_path: str = "./chroma_db") -> VectorDBManager:
    """Initialize the vector database"""
    print(f"💾 Initializing vector database at: {db_path}")
    
    try:
        vdb = VectorDBManager(db_path)
        stats = vdb.get_collection_stats()
        print(f"✅ Vector database initialized")
        print(f"   Collection: {stats['collection_name']}")
        print(f"   Documents: {stats['document_count']}")
        print()
        return vdb
    except Exception as e:
        print(f"❌ Failed to initialize vector database: {e}")
        sys.exit(1)

def process_recipes(llm_client: LocalLLMClient, vdb: VectorDBManager, num_recipes: int = 3) -> List[Dict[str, Any]]:
    """Process random recipes through the LLM and store in vector database"""
    print(f"🍳 Processing {num_recipes} random recipes...")
    
    processed_recipes = []
    
    for i in range(num_recipes):
        print(f"\n📋 Processing recipe {i+1}/{num_recipes}...")
        
        # Get a random recipe
        recipe = get_random_recipe()
        recipe_text = format_recipe_for_summary(recipe)
        
        print(f"   Recipe: {recipe['name']}")
        
        # Generate summary using LLM
        print("   🤖 Generating summary with LLM...")
        summary = llm_client.generate_summary(recipe_text)
        
        if summary:
            print(f"   ✅ Summary generated: {summary[:60]}...")
            
            # Store in vector database
            metadata = {
                "prep_time": recipe["prep_time"],
                "cook_time": recipe["cook_time"],
                "servings": recipe["servings"]
            }
            
            doc_id = vdb.add_recipe_summary(recipe["name"], summary, metadata)
            
            processed_recipes.append({
                "name": recipe["name"],
                "summary": summary,
                "doc_id": doc_id,
                "metadata": metadata
            })
            
        else:
            print("   ❌ Failed to generate summary")
            
        # Small delay between requests to be nice to the LLM
        if i < num_recipes - 1:
            time.sleep(1)
    
    print(f"\n✅ Processed {len(processed_recipes)} recipes successfully")
    return processed_recipes

def test_queries(vdb: VectorDBManager, processed_recipes: List[Dict[str, Any]]):
    """Test querying the vector database"""
    print("\n🔍 Testing vector database queries...")
    
    # Test queries
    test_queries = [
        "chocolate dessert recipe",
        "quick stir fry with vegetables",
        "Italian pizza with cheese",
        "healthy chicken salad",
        "sweet baked goods"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        results = vdb.query_recipes(query, n_results=3)
        
        if results:
            print(f"   Found {len(results)} results:")
            for j, result in enumerate(results[:2]):  # Show top 2 results
                recipe_name = result['metadata'].get('recipe_name', 'Unknown')
                similarity = result['similarity_score']
                print(f"   {j+1}. {recipe_name} (similarity: {similarity:.2f})")
                print(f"      {result['document'][:80]}...")
        else:
            print("   No results found")
    
    print("\n✅ Query testing completed")

def display_database_stats(vdb: VectorDBManager):
    """Display database statistics"""
    print("\n📊 Database Statistics:")
    stats = vdb.get_collection_stats()
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Total Documents: {stats['document_count']}")
    print(f"   Database Path: {stats['db_path']}")
    
    # List all recipes
    recipes = vdb.list_all_recipes()
    if recipes:
        print(f"\n📝 Stored Recipes:")
        for recipe in recipes:
            print(f"   • {recipe['recipe_name']}: {recipe['summary']}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Validate local vector database with LLM integration")
    parser.add_argument("--num-recipes", type=int, default=3, help="Number of recipes to process (default: 3)")
    parser.add_argument("--db-path", default="./chroma_db", help="Path to vector database (default: ./chroma_db)")
    parser.add_argument("--clear-db", action="store_true", help="Clear existing database before starting")
    parser.add_argument("--skip-processing", action="store_true", help="Skip recipe processing, only query existing data")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Initialize LLM client
    try:
        llm_client = LocalLLMClient()
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")
        sys.exit(1)
    
    # Test LLM connection (skip if only querying)
    if not args.skip_processing:
        if not test_llm_connection(llm_client):
            print("\n⚠️  Warning: LLM connection failed. You can still query existing data with --skip-processing")
            sys.exit(1)
    
    # Initialize vector database
    vdb = initialize_vector_db(args.db_path)
    
    # Clear database if requested
    if args.clear_db:
        print("🗑️  Clearing existing database...")
        vdb.clear_collection()
        print("✅ Database cleared")
    
    # Process recipes (unless skipping)
    processed_recipes = []
    if not args.skip_processing:
        processed_recipes = process_recipes(llm_client, vdb, args.num_recipes)
        
        if not processed_recipes:
            print("❌ No recipes were processed successfully")
            sys.exit(1)
    else:
        print("⏭️  Skipping recipe processing")
    
    # Test queries
    test_queries(vdb)
    
    # Display final stats
    display_database_stats(vdb)
    
    print("\n🎉 Vector database validation completed successfully!")
    print("\nNext steps:")
    print("   • Run with --skip-processing to query existing data")
    print("   • Run with --clear-db to start fresh")
    print("   • Adjust --num-recipes to process more data")

if __name__ == "__main__":
    main()