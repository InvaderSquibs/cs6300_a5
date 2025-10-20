#!/usr/bin/env python3
"""
Main execution script for recipe similarity evaluation.

This script demonstrates how to use the recipe similarity evaluation system
to compare recipes and determine if they are similar based on an evaluation model.
"""

import logging
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models import Recipe, SummarizationResponse
from src.comparator import RecipeSimilarityComparator
from config.config import MODEL_NAME, SIMILARITY_THRESHOLD, LOG_LEVEL, LOG_FORMAT


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )


def create_sample_recipes() -> SummarizationResponse:
    """Create sample recipes for demonstration."""
    
    target_recipe = Recipe(
        id="target_001",
        title="Classic Chicken Parmesan",
        description="Crispy breaded chicken topped with marinara sauce and melted cheese",
        ingredients=[
            "4 chicken breasts",
            "1 cup breadcrumbs",
            "1/2 cup parmesan cheese",
            "2 eggs",
            "2 cups marinara sauce",
            "1 cup mozzarella cheese",
            "salt and pepper"
        ],
        instructions=[
            "Pound chicken breasts to even thickness",
            "Set up breading station with flour, beaten eggs, and breadcrumb mixture",
            "Bread each chicken breast thoroughly",
            "Pan fry until golden brown and cooked through",
            "Top with marinara sauce and cheese",
            "Bake until cheese is melted and bubbly"
        ],
        cuisine_type="Italian",
        cooking_time=45,
        serving_size=4
    )
    
    candidate_recipes = [
        Recipe(
            id="candidate_001",
            title="Chicken Parmigiana",
            description="Breaded chicken cutlets with tomato sauce and cheese",
            ingredients=[
                "chicken cutlets",
                "breadcrumbs",
                "parmesan",
                "eggs",
                "tomato sauce",
                "mozzarella"
            ],
            instructions=[
                "Bread the chicken cutlets",
                "Fry until crispy",
                "Add sauce and cheese",
                "Bake until melted"
            ],
            cuisine_type="Italian",
            cooking_time=40
        ),
        Recipe(
            id="candidate_002",
            title="Beef Stir Fry",
            description="Quick beef stir fry with vegetables",
            ingredients=[
                "beef strips",
                "bell peppers",
                "onions",
                "soy sauce",
                "garlic",
                "ginger"
            ],
            instructions=[
                "Heat oil in wok",
                "Stir fry beef until browned",
                "Add vegetables",
                "Season with soy sauce"
            ],
            cuisine_type="Asian",
            cooking_time=20
        ),
        Recipe(
            id="candidate_003",
            title="Crispy Chicken Cutlets",
            description="Golden breaded chicken served with lemon",
            ingredients=[
                "chicken breasts",
                "flour",
                "eggs",
                "breadcrumbs",
                "lemon",
                "oil"
            ],
            instructions=[
                "Flatten chicken breasts",
                "Bread with flour, egg, and breadcrumbs",
                "Fry until golden",
                "Serve with lemon wedges"
            ],
            cuisine_type="American",
            cooking_time=30
        )
    ]
    
    return SummarizationResponse(
        target_recipe=target_recipe,
        candidate_recipes=candidate_recipes,
        query_metadata={"query_type": "recipe_similarity", "timestamp": "2024-01-01T12:00:00Z"}
    )


def main():
    """Main execution function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize the comparator
        logger.info("Starting recipe similarity evaluation...")
        comparator = RecipeSimilarityComparator(
            model_name=MODEL_NAME,
            similarity_threshold=SIMILARITY_THRESHOLD
        )
        
        # Download and load the model
        logger.info("Initializing evaluation model...")
        comparator.initialize()
        
        # Create sample data
        logger.info("Creating sample recipe data...")
        summarization_response = create_sample_recipes()
        
        # Perform comparison
        logger.info("Performing recipe similarity comparison...")
        results = comparator.compare_recipes(summarization_response)
        
        # Display results
        print("\n" + "="*60)
        print("RECIPE SIMILARITY EVALUATION RESULTS")
        print("="*60)
        
        target = summarization_response.target_recipe
        print(f"\nTarget Recipe: {target.title}")
        print(f"Description: {target.description}")
        
        print(f"\nComparison Results (Threshold: {SIMILARITY_THRESHOLD}):")
        print("-" * 50)
        
        for result in results:
            candidate = next(
                r for r in summarization_response.candidate_recipes 
                if r.id == result.candidate_recipe_id
            )
            
            status = "✓ SIMILAR" if result.is_similar else "✗ NOT SIMILAR"
            print(f"\n{candidate.title}")
            print(f"  Similarity Score: {result.similarity_score:.3f}")
            print(f"  Status: {status}")
            print(f"  Description: {candidate.description}")
        
        # Display summary
        summary = comparator.get_similarity_summary(results)
        print(f"\n" + "-" * 50)
        print("SUMMARY:")
        print(f"  Total Comparisons: {summary['total_comparisons']}")
        print(f"  Similar Recipes: {summary['similar_recipes']}")
        print(f"  Similarity Rate: {summary['similarity_rate']:.1%}")
        print(f"  Average Score: {summary['average_similarity_score']:.3f}")
        
        # Model information
        model_info = comparator.get_model_info()
        print(f"\nModel Information:")
        print(f"  Model: {model_info['model_name']}")
        print(f"  Cache Directory: {model_info['cache_dir']}")
        
        # Save results to JSON
        results_data = {
            "target_recipe": target.dict(),
            "results": [result.dict() for result in results],
            "summary": summary,
            "model_info": model_info
        }
        
        output_file = "recipe_similarity_results.json"
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        raise


if __name__ == "__main__":
    main()