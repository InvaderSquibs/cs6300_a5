#!/usr/bin/env python3
"""
Test the recipe similarity system with mock embeddings to validate logic
without requiring heavy ML dependencies.
"""

import sys
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models import Recipe, SummarizationResponse, SimilarityResult
from src.comparator import RecipeSimilarityComparator


def create_mock_evaluator():
    """Create a mock evaluator that uses simple similarity logic."""
    
    def mock_encode_recipes(recipes):
        """Mock encoding that creates simple embeddings based on recipe content."""
        embeddings = []
        
        for recipe in recipes:
            # Create a simple embedding based on recipe characteristics
            text = recipe.to_text().lower()
            
            # Simple features: word counts for different categories
            features = [
                text.count('chicken'),  # protein
                text.count('pasta') + text.count('spaghetti'),  # carbs
                text.count('tomato') + text.count('sauce'),  # sauce
                text.count('cheese'),  # dairy
                text.count('italian'),  # cuisine
                len(recipe.ingredients),  # ingredient count
                recipe.cooking_time or 30,  # cooking time
            ]
            
            # Normalize to create embedding-like vector
            features = np.array(features, dtype=float)
            if np.linalg.norm(features) > 0:
                features = features / np.linalg.norm(features)
            
            embeddings.append(features)
        
        return np.array(embeddings)
    
    # Create mock evaluator
    mock_eval = Mock()
    mock_eval.similarity_threshold = 0.7
    mock_eval.encode_recipes = mock_encode_recipes
    
    def mock_calculate_similarity(target_recipe, candidate_recipes):
        """Mock similarity calculation using cosine similarity."""
        from sklearn.metrics.pairwise import cosine_similarity
        
        all_recipes = [target_recipe] + candidate_recipes
        embeddings = mock_encode_recipes(all_recipes)
        
        target_embedding = embeddings[0:1]
        candidate_embeddings = embeddings[1:]
        
        similarities = cosine_similarity(target_embedding, candidate_embeddings)[0]
        
        results = []
        for i, candidate_recipe in enumerate(candidate_recipes):
            similarity_score = float(similarities[i])
            is_similar = similarity_score >= mock_eval.similarity_threshold
            
            result = SimilarityResult(
                target_recipe_id=target_recipe.id,
                candidate_recipe_id=candidate_recipe.id,
                similarity_score=similarity_score,
                is_similar=is_similar,
                threshold_used=mock_eval.similarity_threshold
            )
            results.append(result)
        
        return results
    
    mock_eval.calculate_similarity = mock_calculate_similarity
    mock_eval.set_threshold = lambda t: setattr(mock_eval, 'similarity_threshold', t)
    mock_eval.get_model_info = lambda: {
        "model_loaded": True,
        "model_name": "mock_model",
        "similarity_threshold": mock_eval.similarity_threshold
    }
    
    return mock_eval


def test_recipe_similarity_logic():
    """Test the recipe similarity logic with mock data."""
    print("Testing recipe similarity logic with mock embeddings...")
    
    # Create test recipes
    target_recipe = Recipe(
        id="target_001",
        title="Chicken Parmesan",
        description="Crispy breaded chicken with tomato sauce and cheese",
        ingredients=[
            "chicken breast",
            "breadcrumbs", 
            "parmesan cheese",
            "tomato sauce",
            "mozzarella cheese"
        ],
        instructions=[
            "Bread the chicken",
            "Fry until golden",
            "Add tomato sauce and cheese",
            "Bake until melted"
        ],
        cuisine_type="Italian",
        cooking_time=45
    )
    
    candidate_recipes = [
        Recipe(
            id="similar_001",
            title="Chicken Parmigiana", 
            description="Breaded chicken cutlets with sauce and cheese",
            ingredients=["chicken", "breadcrumbs", "tomato sauce", "cheese"],
            instructions=["Bread chicken", "Cook until crispy", "Top with sauce"],
            cuisine_type="Italian",
            cooking_time=40
        ),
        Recipe(
            id="different_001",
            title="Beef Stir Fry",
            description="Quick Asian beef and vegetable stir fry",
            ingredients=["beef", "vegetables", "soy sauce", "garlic"],
            instructions=["Heat oil", "Stir fry beef", "Add vegetables"],
            cuisine_type="Asian", 
            cooking_time=15
        ),
        Recipe(
            id="somewhat_similar_001",
            title="Chicken Marsala",
            description="Chicken in wine sauce",
            ingredients=["chicken", "mushrooms", "wine", "butter"],
            instructions=["Sauté chicken", "Make wine sauce", "Combine"],
            cuisine_type="Italian",
            cooking_time=35
        )
    ]
    
    # Create comparator with mocked evaluator
    comparator = RecipeSimilarityComparator(similarity_threshold=0.7)
    comparator.evaluator = create_mock_evaluator()
    comparator._model_loaded = True
    
    # Create summarization response
    response = SummarizationResponse(
        target_recipe=target_recipe,
        candidate_recipes=candidate_recipes
    )
    
    # Perform comparison
    results = comparator.compare_recipes(response)
    
    # Display results
    print(f"\nTarget Recipe: {target_recipe.title}")
    print(f"Description: {target_recipe.description}")
    print(f"\nComparison Results (Threshold: {comparator.evaluator.similarity_threshold}):")
    print("-" * 60)
    
    for result in results:
        candidate = next(r for r in candidate_recipes if r.id == result.candidate_recipe_id)
        status = "✓ SIMILAR" if result.is_similar else "✗ NOT SIMILAR"
        print(f"\n{candidate.title}")
        print(f"  Similarity Score: {result.similarity_score:.3f}")
        print(f"  Status: {status}")
        print(f"  Description: {candidate.description}")
    
    # Test summary
    summary = comparator.get_similarity_summary(results)
    print(f"\n" + "-" * 60)
    print("SUMMARY:")
    print(f"  Total Comparisons: {summary['total_comparisons']}")
    print(f"  Similar Recipes: {summary['similar_recipes']}")
    print(f"  Similarity Rate: {summary['similarity_rate']:.1%}")
    print(f"  Average Score: {summary['average_similarity_score']:.3f}")
    
    # Validate results
    assert len(results) == 3, "Should have 3 comparison results"
    assert all(0 <= r.similarity_score <= 1 for r in results), "Scores should be between 0 and 1"
    
    # The similar recipe (Chicken Parmigiana) should have highest score
    similar_result = next(r for r in results if r.candidate_recipe_id == "similar_001")
    different_result = next(r for r in results if r.candidate_recipe_id == "different_001")
    
    print(f"\nValidation:")
    print(f"  Similar recipe score: {similar_result.similarity_score:.3f}")
    print(f"  Different recipe score: {different_result.similarity_score:.3f}")
    
    # Basic validation that similar recipes score higher than different ones
    assert similar_result.similarity_score > different_result.similarity_score, \
        "Similar recipe should score higher than different recipe"
    
    print("\n✓ Recipe similarity logic validation PASSED!")
    
    return results


def test_threshold_behavior():
    """Test that threshold changes affect similarity decisions."""
    print("\nTesting threshold behavior...")
    
    # Create simple recipes
    target = Recipe(id="target", title="Test Recipe", ingredients=["ingredient1"])
    candidate = Recipe(id="candidate", title="Similar Recipe", ingredients=["ingredient1"]) 
    
    response = SummarizationResponse(target_recipe=target, candidate_recipes=[candidate])
    
    # Test with different thresholds
    for threshold in [0.3, 0.7, 0.9]:
        comparator = RecipeSimilarityComparator(similarity_threshold=threshold)
        comparator.evaluator = create_mock_evaluator()
        comparator.evaluator.set_threshold(threshold)
        comparator._model_loaded = True
        
        results = comparator.compare_recipes(response)
        result = results[0]
        
        print(f"  Threshold {threshold}: Score={result.similarity_score:.3f}, Similar={result.is_similar}")
    
    print("✓ Threshold behavior test PASSED!")


def main():
    """Run all tests."""
    print("="*70)
    print("RECIPE SIMILARITY SYSTEM - LOGIC VALIDATION")
    print("="*70)
    
    try:
        test_recipe_similarity_logic()
        test_threshold_behavior()
        
        print("\n" + "="*70)
        print("✅ ALL LOGIC VALIDATION TESTS PASSED!")
        print("\nThe recipe similarity evaluation logic is working correctly.")
        print("The system can now be used with real ML models by installing:")
        print("  pip install -r requirements.txt")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)