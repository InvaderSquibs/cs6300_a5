"""Utility functions for handling recipe data and JSON operations."""

import json
import logging
from typing import List, Dict, Any, Union
from pathlib import Path

from src.models import Recipe, SummarizationResponse, SimilarityResult


logger = logging.getLogger(__name__)


def load_recipes_from_json(file_path: Union[str, Path]) -> SummarizationResponse:
    """
    Load recipes from a JSON file.
    
    Expected JSON format:
    {
        "target_recipe": {recipe_data},
        "candidate_recipes": [{recipe_data}, ...],
        "query_metadata": {optional_metadata}
    }
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        SummarizationResponse object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON format is invalid
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        if "target_recipe" not in data:
            raise ValueError("Missing 'target_recipe' in JSON data")
        if "candidate_recipes" not in data:
            raise ValueError("Missing 'candidate_recipes' in JSON data")
        
        # Create Recipe objects
        target_recipe = Recipe(**data["target_recipe"])
        candidate_recipes = [Recipe(**recipe_data) for recipe_data in data["candidate_recipes"]]
        
        query_metadata = data.get("query_metadata", {})
        
        return SummarizationResponse(
            target_recipe=target_recipe,
            candidate_recipes=candidate_recipes,
            query_metadata=query_metadata
        )
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing recipe data: {e}")


def save_results_to_json(
    results: List[SimilarityResult],
    target_recipe: Recipe,
    candidate_recipes: List[Recipe],
    output_path: Union[str, Path],
    include_summary: bool = True
) -> None:
    """
    Save similarity results to a JSON file.
    
    Args:
        results: List of similarity results
        target_recipe: The target recipe
        candidate_recipes: List of candidate recipes
        output_path: Path to save the JSON file
        include_summary: Whether to include summary statistics
    """
    output_path = Path(output_path)
    
    # Prepare data structure
    data = {
        "target_recipe": target_recipe.dict(),
        "candidate_recipes": [recipe.dict() for recipe in candidate_recipes],
        "similarity_results": [result.dict() for result in results],
        "timestamp": str(Path().cwd())  # Simple timestamp placeholder
    }
    
    if include_summary and results:
        # Calculate summary statistics
        similar_count = sum(1 for result in results if result.is_similar)
        similarity_scores = [result.similarity_score for result in results]
        
        data["summary"] = {
            "total_comparisons": len(results),
            "similar_recipes": similar_count,
            "dissimilar_recipes": len(results) - similar_count,
            "similarity_rate": similar_count / len(results),
            "average_similarity_score": sum(similarity_scores) / len(similarity_scores),
            "max_similarity_score": max(similarity_scores),
            "min_similarity_score": min(similarity_scores),
            "threshold_used": results[0].threshold_used if results else None
        }
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to: {output_path}")


def create_sample_json_file(output_path: Union[str, Path]) -> None:
    """
    Create a sample JSON file with recipe data for testing.
    
    Args:
        output_path: Path to save the sample JSON file
    """
    sample_data = {
        "target_recipe": {
            "id": "target_001",
            "title": "Classic Margherita Pizza",
            "description": "Traditional Neapolitan pizza with fresh mozzarella and basil",
            "ingredients": [
                "pizza dough",
                "San Marzano tomatoes",
                "fresh mozzarella",
                "fresh basil",
                "extra virgin olive oil",
                "salt"
            ],
            "instructions": [
                "Prepare pizza dough and let rise",
                "Stretch dough into round shape",
                "Spread tomato sauce evenly",
                "Add torn mozzarella pieces",
                "Bake in very hot oven until crust is golden",
                "Garnish with fresh basil and olive oil"
            ],
            "cuisine_type": "Italian",
            "cooking_time": 25,
            "serving_size": 2
        },
        "candidate_recipes": [
            {
                "id": "candidate_001",
                "title": "Margherita Pizza",
                "description": "Simple pizza with tomato, mozzarella, and basil",
                "ingredients": [
                    "pizza base",
                    "tomato sauce",
                    "mozzarella cheese",
                    "basil leaves",
                    "olive oil"
                ],
                "instructions": [
                    "Roll out pizza dough",
                    "Apply tomato sauce",
                    "Add cheese and basil",
                    "Bake until crispy"
                ],
                "cuisine_type": "Italian",
                "cooking_time": 20
            },
            {
                "id": "candidate_002",
                "title": "Pepperoni Pizza",
                "description": "Classic American pizza with pepperoni and cheese",
                "ingredients": [
                    "pizza dough",
                    "pizza sauce",
                    "mozzarella cheese",
                    "pepperoni slices"
                ],
                "instructions": [
                    "Spread sauce on dough",
                    "Add cheese and pepperoni",
                    "Bake until golden"
                ],
                "cuisine_type": "American",
                "cooking_time": 18
            },
            {
                "id": "candidate_003",
                "title": "Chicken Curry",
                "description": "Spicy Indian chicken curry with aromatic spices",
                "ingredients": [
                    "chicken pieces",
                    "onions",
                    "tomatoes",
                    "garlic",
                    "ginger",
                    "curry spices",
                    "coconut milk"
                ],
                "instructions": [
                    "Sauté onions until golden",
                    "Add garlic, ginger, and spices",
                    "Add chicken and brown",
                    "Add tomatoes and coconut milk",
                    "Simmer until chicken is cooked"
                ],
                "cuisine_type": "Indian",
                "cooking_time": 40
            }
        ],
        "query_metadata": {
            "query_type": "recipe_similarity_evaluation",
            "timestamp": "2024-01-01T12:00:00Z",
            "source": "sample_data_generator"
        }
    }
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Sample JSON file created: {output_path}")


def validate_recipe_json(file_path: Union[str, Path]) -> bool:
    """
    Validate that a JSON file contains properly formatted recipe data.
    
    Args:
        file_path: Path to the JSON file to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        load_recipes_from_json(file_path)
        return True
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Validation failed: {e}")
        return False