"""Unit tests for data processing utilities."""

import pytest
import json
import tempfile
import os
from vector_template.utils.data_processing import (
    preprocess_recipe_text,
    extract_recipe_metadata,
    chunk_large_recipe,
    format_search_results,
    load_recipes_from_json,
)


class TestDataProcessing:
    """Test cases for data processing utilities."""
    
    def test_preprocess_recipe_text(self, sample_recipes):
        """Test recipe text preprocessing."""
        recipe = sample_recipes[0]
        text = preprocess_recipe_text(recipe)
        
        assert "Recipe: Test Pasta" in text
        assert "pasta" in text.lower()
        assert "tomatoes" in text.lower()
        assert "Cook pasta" in text
    
    def test_extract_recipe_metadata(self, sample_recipes):
        """Test recipe metadata extraction."""
        recipe = sample_recipes[0]
        metadata = extract_recipe_metadata(recipe)
        
        assert metadata["type"] == "recipe"
        assert metadata["name"] == "Test Pasta"
        assert metadata["cuisine"] == "Italian"
        assert metadata["prep_time"] == "10 minutes"
        assert metadata["ingredient_count"] == 3
    
    def test_chunk_large_recipe(self):
        """Test chunking of large recipes."""
        large_recipe = {
            "id": "large_recipe",
            "name": "Very Long Recipe Name That Goes On And On",
            "description": "A very long description " * 20,  # Make it long
            "ingredients": ["ingredient " + str(i) for i in range(50)],  # Many ingredients
            "instructions": "Step " + str(i) + ": Do something. " for i in range(100),  # Long instructions
        }
        
        chunks = chunk_large_recipe(large_recipe, max_chunk_size=500)
        
        assert len(chunks) > 1  # Should be split into multiple chunks
        assert all(len(chunk["text"]) <= 500 for chunk in chunks)
        assert all("chunk_type" in chunk["metadata"] for chunk in chunks)
    
    def test_format_search_results(self):
        """Test search results formatting."""
        # Mock search results
        results = {
            "documents": [["Recipe for pasta", "Recipe for cake"]],
            "metadatas": [[{"name": "Pasta Recipe"}, {"name": "Cake Recipe"}]],
            "distances": [[0.1, 0.2]],
            "ids": [["pasta_1", "cake_1"]]
        }
        
        formatted = format_search_results(results, max_results=2)
        
        assert "Pasta Recipe" in formatted
        assert "Cake Recipe" in formatted
        assert "pasta_1" in formatted
        assert "cake_1" in formatted
    
    def test_format_empty_search_results(self):
        """Test formatting of empty search results."""
        empty_results = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
            "ids": [[]]
        }
        
        formatted = format_search_results(empty_results)
        assert "No results found" in formatted
    
    def test_load_recipes_from_json(self):
        """Test loading recipes from JSON file."""
        # Create temporary JSON file
        test_recipes = [
            {
                "name": "Test Recipe 1",
                "ingredients": ["ingredient1", "ingredient2"],
                "instructions": "Do something"
            },
            {
                "name": "Test Recipe 2",
                "ingredients": ["ingredient3", "ingredient4"],
                "instructions": "Do something else"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_recipes, f)
            temp_file = f.name
        
        try:
            loaded_recipes = load_recipes_from_json(temp_file)
            
            assert len(loaded_recipes) == 2
            assert loaded_recipes[0]["name"] == "Test Recipe 1"
            assert "id" in loaded_recipes[0]  # Should have auto-generated ID
            assert loaded_recipes[1]["name"] == "Test Recipe 2"
        finally:
            os.unlink(temp_file)
    
    def test_load_recipes_from_json_with_wrapper(self):
        """Test loading recipes from JSON with wrapper object."""
        test_data = {
            "recipes": [
                {"name": "Recipe A", "ingredients": ["a", "b"]},
                {"name": "Recipe B", "ingredients": ["c", "d"]}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            loaded_recipes = load_recipes_from_json(temp_file)
            
            assert len(loaded_recipes) == 2
            assert loaded_recipes[0]["name"] == "Recipe A"
        finally:
            os.unlink(temp_file)
    
    def test_preprocess_recipe_text_missing_fields(self):
        """Test preprocessing with missing recipe fields."""
        minimal_recipe = {
            "name": "Minimal Recipe"
        }
        
        text = preprocess_recipe_text(minimal_recipe)
        assert "Recipe: Minimal Recipe" in text
        # Should not crash with missing fields
    
    def test_extract_metadata_missing_fields(self):
        """Test metadata extraction with missing fields."""
        minimal_recipe = {
            "name": "Minimal Recipe"
        }
        
        metadata = extract_recipe_metadata(minimal_recipe)
        assert metadata["type"] == "recipe"
        assert metadata["name"] == "Minimal Recipe"
        # Should handle missing fields gracefully