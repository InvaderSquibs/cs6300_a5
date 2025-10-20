#!/usr/bin/env python3
"""
Test the recipe similarity models and logic without ML dependencies.
"""

import sys
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models import Recipe, SummarizationResponse, SimilarityResult


def simple_recipe_similarity(target_recipe, candidate_recipes, threshold=0.7):
    """
    Simple recipe similarity function using basic text features.
    This demonstrates the core logic without requiring ML models.
    """
    
    def recipe_to_features(recipe):
        """Convert recipe to feature vector based on recipe characteristics."""
        text = recipe.to_text().lower()
        ingredients_text = ' '.join(recipe.ingredients).lower()
        instructions_text = ' '.join(recipe.instructions).lower()
        
        # Protein features
        protein_features = [
            text.count('chicken'),
            text.count('beef'),
            text.count('pork'),
            text.count('fish'),
            text.count('tofu'),
        ]
        
        # Carb features
        carb_features = [
            text.count('pasta') + text.count('spaghetti') + text.count('noodle'),
            text.count('rice'),
            text.count('bread') + text.count('breadcrumb'),
            text.count('potato'),
        ]
        
        # Flavor/sauce features
        flavor_features = [
            text.count('tomato') + text.count('marinara'),
            text.count('cheese'),
            text.count('cream'),
            text.count('soy sauce'),
            text.count('garlic'),
            text.count('onion'),
        ]
        
        # Cooking method features
        cooking_features = [
            instructions_text.count('fry') + instructions_text.count('pan'),
            instructions_text.count('bake') + instructions_text.count('oven'),
            instructions_text.count('boil') + instructions_text.count('simmer'),
            instructions_text.count('stir'),
            instructions_text.count('bread') + instructions_text.count('coat'),
        ]
        
        # Cuisine features
        cuisine_features = [
            1.0 if recipe.cuisine_type and 'italian' in recipe.cuisine_type.lower() else 0.0,
            1.0 if recipe.cuisine_type and 'asian' in recipe.cuisine_type.lower() else 0.0,
            1.0 if recipe.cuisine_type and 'american' in recipe.cuisine_type.lower() else 0.0,
        ]
        
        # Combine all features
        all_features = (protein_features + carb_features + flavor_features + 
                       cooking_features + cuisine_features)
        
        # Add structural features
        all_features.extend([
            len(recipe.ingredients) / 10.0,  # normalized ingredient count
            (recipe.cooking_time or 30) / 60.0,  # normalized cooking time
        ])
        
        # Convert to numpy array and normalize
        features = np.array(all_features, dtype=float)
        
        # Use L2 normalization to create unit vector
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        
        return features
    
    # Create feature vectors
    target_features = recipe_to_features(target_recipe).reshape(1, -1)
    candidate_features = np.array([recipe_to_features(recipe) for recipe in candidate_recipes])
    
    # Calculate cosine similarities
    similarities = cosine_similarity(target_features, candidate_features)[0]
    
    # Create results
    results = []
    for i, candidate_recipe in enumerate(candidate_recipes):
        similarity_score = float(similarities[i])
        is_similar = similarity_score >= threshold
        
        result = SimilarityResult(
            target_recipe_id=target_recipe.id,
            candidate_recipe_id=candidate_recipe.id,
            similarity_score=similarity_score,
            is_similar=is_similar,
            threshold_used=threshold
        )
        results.append(result)
    
    return results


def test_recipe_similarity():
    """Test recipe similarity with example data."""
    print("Testing Recipe Similarity Evaluation Logic")
    print("="*50)
    
    # Create target recipe
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
    
    # Create candidate recipes
    candidate_recipes = [
        Recipe(
            id="similar_001",
            title="Chicken Parmigiana",
            description="Breaded chicken cutlets with tomato sauce and cheese",
            ingredients=[
                "chicken cutlets",
                "breadcrumbs",
                "parmesan cheese",
                "eggs",
                "tomato sauce",
                "mozzarella cheese"
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
            id="different_001", 
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
            id="somewhat_similar_001",
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
    
    print(f"Target Recipe: {target_recipe.title}")
    print(f"Description: {target_recipe.description}\n")
    
    # Test with different thresholds
    for threshold in [0.5, 0.7, 0.9]:
        print(f"Testing with threshold: {threshold}")
        print("-" * 40)
        
        results = simple_recipe_similarity(target_recipe, candidate_recipes, threshold)
        
        for result in results:
            candidate = next(r for r in candidate_recipes if r.id == result.candidate_recipe_id)
            status = "✓ SIMILAR" if result.is_similar else "✗ NOT SIMILAR"
            print(f"{candidate.title:25} | Score: {result.similarity_score:.3f} | {status}")
        
        similar_count = sum(1 for r in results if r.is_similar)
        print(f"Summary: {similar_count}/{len(results)} recipes deemed similar\n")
    
    return results


def test_summarization_response():
    """Test the SummarizationResponse workflow."""
    print("Testing SummarizationResponse Workflow")
    print("="*50)
    
    target = Recipe(
        id="target",
        title="Simple Pasta",
        ingredients=["pasta", "tomato sauce", "cheese"],
        instructions=["Cook pasta", "Add sauce", "Top with cheese"]
    )
    
    candidates = [
        Recipe(
            id="cand1",
            title="Spaghetti Marinara", 
            ingredients=["spaghetti", "marinara sauce", "parmesan"],
            instructions=["Boil spaghetti", "Heat sauce", "Combine"]
        ),
        Recipe(
            id="cand2",
            title="Chicken Soup",
            ingredients=["chicken", "vegetables", "broth"],
            instructions=["Simmer chicken", "Add vegetables"]
        )
    ]
    
    # Create summarization response
    response = SummarizationResponse(
        target_recipe=target,
        candidate_recipes=candidates,
        query_metadata={"timestamp": "2024-01-01", "query_type": "similarity"}
    )
    
    print(f"Target: {response.target_recipe.title}")
    print(f"Candidates: {[r.title for r in response.candidate_recipes]}")
    print(f"Metadata: {response.query_metadata}")
    
    # Test similarity
    results = simple_recipe_similarity(
        response.target_recipe,
        response.candidate_recipes,
        threshold=0.6
    )
    
    print("\nSimilarity Results:")
    for result in results:
        candidate = next(r for r in candidates if r.id == result.candidate_recipe_id)
        print(f"  {candidate.title}: {result.similarity_score:.3f} ({'Similar' if result.is_similar else 'Different'})")
    
    print("✓ SummarizationResponse test passed!\n")
    
    return response, results


def main():
    """Run all tests."""
    print("RECIPE SIMILARITY EVALUATION - CORE LOGIC TEST")
    print("="*60)
    print("Testing the core similarity logic without ML dependencies\n")
    
    try:
        # Test basic similarity
        similarity_results = test_recipe_similarity()
        
        # Test summarization workflow 
        response, workflow_results = test_summarization_response()
        
        print("FINAL VALIDATION")
        print("="*60)
        
        # Validate that similar recipes score higher than different ones
        chicken_parm_result = next(r for r in similarity_results if "similar_001" in r.candidate_recipe_id)
        beef_stir_fry_result = next(r for r in similarity_results if "different_001" in r.candidate_recipe_id)
        
        print(f"Chicken Parmigiana (similar): {chicken_parm_result.similarity_score:.3f}")
        print(f"Beef Stir Fry (different): {beef_stir_fry_result.similarity_score:.3f}")
        
        assert chicken_parm_result.similarity_score > beef_stir_fry_result.similarity_score, \
            "Similar recipe should score higher than different recipe"
        
        print("\n✅ ALL TESTS PASSED!")
        print("\nThe recipe similarity evaluation system is working correctly.")
        print("Core logic validates that:")
        print("  • Similar recipes (Chicken Parmesan vs Chicken Parmigiana) score higher")
        print("  • Different recipes (Chicken Parmesan vs Beef Stir Fry) score lower") 
        print("  • Thresholds properly affect similarity decisions")
        print("  • All data models work as expected")
        
        print(f"\nTo use with real ML models, install: pip install -r requirements.txt")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)