"""Simple validation script to test core functionality without ML dependencies."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_models():
    """Test basic model functionality."""
    print("Testing data models...")
    
    from src.models import Recipe, SummarizationResponse, SimilarityResult
    
    # Test Recipe creation
    recipe = Recipe(
        id="test_001",
        title="Test Recipe",
        ingredients=["flour", "sugar", "eggs"],
        instructions=["Mix ingredients", "Bake for 30 minutes"],
        description="A simple test recipe",
        cuisine_type="American",
        cooking_time=30
    )
    
    assert recipe.id == "test_001"
    assert recipe.title == "Test Recipe"
    assert len(recipe.ingredients) == 3
    assert "flour" in recipe.ingredients
    
    # Test text conversion
    text = recipe.to_text()
    assert "Test Recipe" in text
    assert "flour" in text
    assert "Mix ingredients" in text
    
    print("✓ Recipe model works correctly")
    
    # Test SummarizationResponse
    target = Recipe(id="target", title="Target Recipe")
    candidates = [
        Recipe(id="cand1", title="Candidate 1"),
        Recipe(id="cand2", title="Candidate 2")
    ]
    
    response = SummarizationResponse(
        target_recipe=target,
        candidate_recipes=candidates,
        query_metadata={"test": True}
    )
    
    assert response.target_recipe.id == "target"
    assert len(response.candidate_recipes) == 2
    assert response.query_metadata["test"] is True
    
    print("✓ SummarizationResponse model works correctly")
    
    # Test SimilarityResult
    result = SimilarityResult(
        target_recipe_id="target",
        candidate_recipe_id="candidate",
        similarity_score=0.85,
        is_similar=True,
        threshold_used=0.7
    )
    
    assert result.similarity_score == 0.85
    assert result.is_similar is True
    assert result.threshold_used == 0.7
    
    print("✓ SimilarityResult model works correctly")
    
    return True


def test_utils():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    from src.utils import create_sample_json_file, validate_recipe_json
    import tempfile
    import os
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Test sample file creation
        create_sample_json_file(temp_file)
        assert os.path.exists(temp_file)
        print("✓ Sample JSON file creation works")
        
        # Test validation
        is_valid = validate_recipe_json(temp_file)
        assert is_valid is True
        print("✓ JSON validation works")
        
        # Test loading (this will test the full pipeline)
        from src.utils import load_recipes_from_json
        response = load_recipes_from_json(temp_file)
        assert response.target_recipe is not None
        assert len(response.candidate_recipes) > 0
        print("✓ JSON loading works")
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    return True


def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    from config.config import MODEL_NAME, SIMILARITY_THRESHOLD
    
    assert MODEL_NAME is not None
    assert isinstance(SIMILARITY_THRESHOLD, float)
    assert 0 <= SIMILARITY_THRESHOLD <= 1
    
    print(f"✓ Configuration loaded: model={MODEL_NAME}, threshold={SIMILARITY_THRESHOLD}")
    
    return True


def main():
    """Run all validation tests."""
    print("="*60)
    print("RECIPE SIMILARITY SYSTEM VALIDATION")
    print("="*60)
    
    try:
        # Test each component
        test_models()
        test_utils()
        test_configuration()
        
        print("\n" + "="*60)
        print("✓ ALL VALIDATION TESTS PASSED!")
        print("The recipe similarity evaluation system is ready to use.")
        print("\nTo run with ML models, install dependencies with:")
        print("  pip install -r requirements.txt")
        print("\nThen run the demo with:")
        print("  python main.py")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)