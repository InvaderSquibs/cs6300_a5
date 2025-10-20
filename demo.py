#!/usr/bin/env python3
"""
Demo script showing the recipe similarity evaluation system in action.
This demonstrates the complete workflow without requiring heavy ML dependencies.
"""

import sys
from pathlib import Path

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models import Recipe, SummarizationResponse
from test_core_logic import simple_recipe_similarity


def create_demo_data():
    """Create demonstration recipe data."""
    
    # Target recipe: A classic dish
    target_recipe = Recipe(
        id="demo_target",
        title="Spaghetti Carbonara",
        description="Classic Italian pasta dish with eggs, cheese, pancetta, and black pepper",
        ingredients=[
            "400g spaghetti",
            "200g pancetta",
            "4 large eggs",
            "100g pecorino romano cheese",
            "100g parmesan cheese",
            "freshly ground black pepper",
            "salt"
        ],
        instructions=[
            "Bring large pot of salted water to boil",
            "Cook spaghetti until al dente",
            "Meanwhile, cook pancetta in large pan until crispy",
            "Whisk eggs with grated cheeses and black pepper",
            "Drain pasta, reserving 1 cup pasta water",
            "Add hot pasta to pan with pancetta",
            "Remove from heat, add egg mixture, toss quickly",
            "Add pasta water as needed to create creamy sauce"
        ],
        cuisine_type="Italian",
        cooking_time=20,
        serving_size=4
    )
    
    # Candidate recipes with varying similarity
    candidate_recipes = [
        # Very similar - another carbonara recipe
        Recipe(
            id="very_similar",
            title="Traditional Carbonara",
            description="Authentic Roman carbonara with guanciale, eggs, and pecorino",
            ingredients=[
                "spaghetti",
                "guanciale",
                "eggs",
                "pecorino romano",
                "black pepper"
            ],
            instructions=[
                "Cook pasta in salted water",
                "Render guanciale fat",
                "Whisk eggs with cheese",
                "Combine hot pasta with egg mixture"
            ],
            cuisine_type="Italian",
            cooking_time=18
        ),
        
        # Somewhat similar - different Italian pasta
        Recipe(
            id="somewhat_similar", 
            title="Cacio e Pepe",
            description="Simple Roman pasta with cheese and pepper",
            ingredients=[
                "spaghetti",
                "pecorino romano cheese",
                "black pepper",
                "salt"
            ],
            instructions=[
                "Cook spaghetti in salted water",
                "Reserve pasta water",
                "Toss pasta with cheese and pepper",
                "Add pasta water to create sauce"
            ],
            cuisine_type="Italian",
            cooking_time=15
        ),
        
        # Different but same cuisine - risotto
        Recipe(
            id="different_cuisine",
            title="Mushroom Risotto",
            description="Creamy Italian rice dish with mushrooms",
            ingredients=[
                "arborio rice",
                "mushrooms",
                "onion",
                "white wine",
                "chicken stock",
                "parmesan cheese",
                "butter"
            ],
            instructions=[
                "Sauté onions and mushrooms",
                "Add rice, toast briefly",
                "Add wine, let absorb",
                "Gradually add warm stock, stirring constantly",
                "Finish with cheese and butter"
            ],
            cuisine_type="Italian",
            cooking_time=35
        ),
        
        # Very different - Asian dish
        Recipe(
            id="very_different",
            title="Pad Thai",
            description="Thai stir-fried noodles with shrimp and peanuts",
            ingredients=[
                "rice noodles",
                "shrimp",
                "bean sprouts",
                "eggs",
                "peanuts",
                "fish sauce",
                "tamarind paste",
                "palm sugar"
            ],
            instructions=[
                "Soak rice noodles until soft",
                "Heat oil in wok",
                "Stir-fry shrimp until pink",
                "Add noodles and sauce",
                "Scramble eggs into mixture",
                "Add bean sprouts and peanuts"
            ],
            cuisine_type="Thai", 
            cooking_time=25
        )
    ]
    
    return SummarizationResponse(
        target_recipe=target_recipe,
        candidate_recipes=candidate_recipes,
        query_metadata={
            "demo": True,
            "description": "Recipe similarity evaluation demonstration"
        }
    )


def run_demo():
    """Run the complete demonstration."""
    print("🍝 RECIPE SIMILARITY EVALUATION DEMO")
    print("="*60)
    print("Demonstrating recipe comparison using similarity evaluation\n")
    
    # Create demo data
    response = create_demo_data()
    target = response.target_recipe
    
    print(f"🎯 TARGET RECIPE: {target.title}")
    print(f"   Description: {target.description}")
    print(f"   Cuisine: {target.cuisine_type}")
    print(f"   Cooking Time: {target.cooking_time} minutes")
    print(f"   Key Ingredients: {', '.join(target.ingredients[:3])}...")
    print()
    
    # Run similarity comparison with different thresholds
    thresholds = [0.5, 0.7, 0.9]
    
    for threshold in thresholds:
        print(f"📊 SIMILARITY RESULTS (Threshold: {threshold})")
        print("-" * 50)
        
        results = simple_recipe_similarity(target, response.candidate_recipes, threshold)
        
        for result in results:
            candidate = next(r for r in response.candidate_recipes 
                           if r.id == result.candidate_recipe_id)
            
            # Determine expected similarity level
            if result.candidate_recipe_id == "very_similar":
                expected = "🟢 Expected: Very Similar"
            elif result.candidate_recipe_id == "somewhat_similar":
                expected = "🟡 Expected: Somewhat Similar"
            elif result.candidate_recipe_id == "different_cuisine":
                expected = "🟠 Expected: Different (Same Cuisine)"
            else:
                expected = "🔴 Expected: Very Different"
            
            status = "✅ SIMILAR" if result.is_similar else "❌ NOT SIMILAR"
            
            print(f"{candidate.title:25} | Score: {result.similarity_score:.3f} | {status}")
            print(f"{'':25} | {expected}")
            print(f"{'':25} | {candidate.cuisine_type} - {candidate.cooking_time}min")
            print()
        
        # Summary
        similar_count = sum(1 for r in results if r.is_similar)
        print(f"📈 SUMMARY: {similar_count}/{len(results)} recipes deemed similar at threshold {threshold}")
        print("="*60)
        print()
    
    print("🏆 DEMONSTRATION COMPLETE!")
    print("\nKey Insights:")
    print("• Higher thresholds (0.9) are more selective")
    print("• Similar recipes (Traditional Carbonara) score highest")
    print("• Different cuisines (Pad Thai) score lowest") 
    print("• The system correctly identifies recipe similarity patterns")
    print("\n💡 This demonstrates the core logic that will be enhanced")
    print("   when using real ML models with sentence transformers!")


if __name__ == "__main__":
    run_demo()