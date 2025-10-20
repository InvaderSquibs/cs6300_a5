"""Tests for recipe similarity evaluation system."""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models import Recipe, SummarizationResponse
from src.evaluator import EvaluationModel
from src.comparator import RecipeSimilarityComparator


class TestRecipeModels(unittest.TestCase):
    """Test recipe data models."""
    
    def test_recipe_creation(self):
        """Test recipe creation and text conversion."""
        recipe = Recipe(
            id="test_001",
            title="Test Recipe",
            ingredients=["ingredient1", "ingredient2"],
            instructions=["step1", "step2"],
            description="A test recipe"
        )
        
        self.assertEqual(recipe.id, "test_001")
        self.assertEqual(recipe.title, "Test Recipe")
        self.assertEqual(len(recipe.ingredients), 2)
        
        # Test text conversion
        text = recipe.to_text()
        self.assertIn("Test Recipe", text)
        self.assertIn("ingredient1", text)
        self.assertIn("step1", text)
    
    def test_summarization_response(self):
        """Test summarization response model."""
        target = Recipe(id="target", title="Target Recipe")
        candidates = [
            Recipe(id="cand1", title="Candidate 1"),
            Recipe(id="cand2", title="Candidate 2")
        ]
        
        response = SummarizationResponse(
            target_recipe=target,
            candidate_recipes=candidates
        )
        
        self.assertEqual(response.target_recipe.id, "target")
        self.assertEqual(len(response.candidate_recipes), 2)


class TestEvaluationModel(unittest.TestCase):
    """Test evaluation model functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.model = EvaluationModel(
            model_name="all-MiniLM-L6-v2",
            cache_dir=self.temp_dir,
            similarity_threshold=0.5
        )
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_model_initialization(self):
        """Test model initialization."""
        self.assertEqual(self.model.similarity_threshold, 0.5)
        self.assertEqual(self.model.cache_dir, self.temp_dir)
        self.assertIsNone(self.model.model)
    
    def test_threshold_setting(self):
        """Test threshold setting."""
        self.model.set_threshold(0.8)
        self.assertEqual(self.model.similarity_threshold, 0.8)
        
        with self.assertRaises(ValueError):
            self.model.set_threshold(-0.1)
        
        with self.assertRaises(ValueError):
            self.model.set_threshold(1.5)


class TestRecipeSimilarityComparator(unittest.TestCase):
    """Test recipe similarity comparator."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.comparator = RecipeSimilarityComparator(
            cache_dir=self.temp_dir,
            similarity_threshold=0.5
        )
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_comparator_initialization(self):
        """Test comparator initialization."""
        self.assertFalse(self.comparator._model_loaded)
        
        model_info = self.comparator.get_model_info()
        self.assertFalse(model_info["model_loaded"])
    
    def test_threshold_setting(self):
        """Test threshold setting."""
        self.comparator.set_similarity_threshold(0.9)
        self.assertEqual(self.comparator.evaluator.similarity_threshold, 0.9)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test recipes
        self.target_recipe = Recipe(
            id="target",
            title="Spaghetti Carbonara",
            ingredients=["spaghetti", "eggs", "bacon", "parmesan", "black pepper"],
            instructions=["Cook pasta", "Mix eggs and cheese", "Combine with hot pasta"],
            description="Classic Italian pasta dish"
        )
        
        self.similar_recipe = Recipe(
            id="similar",
            title="Pasta Carbonara",
            ingredients=["pasta", "eggs", "pancetta", "pecorino romano", "pepper"],
            instructions=["Boil pasta", "Whisk eggs with cheese", "Toss with pasta"],
            description="Traditional carbonara recipe"
        )
        
        self.different_recipe = Recipe(
            id="different",
            title="Chocolate Cake",
            ingredients=["flour", "sugar", "cocoa", "eggs", "butter"],
            instructions=["Mix dry ingredients", "Add wet ingredients", "Bake"],
            description="Rich chocolate cake"
        )
    
    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        from src.models import SimilarityResult
        
        results = [
            SimilarityResult(
                target_recipe_id="target",
                candidate_recipe_id="cand1",
                similarity_score=0.8,
                is_similar=True,
                threshold_used=0.7
            ),
            SimilarityResult(
                target_recipe_id="target",
                candidate_recipe_id="cand2",
                similarity_score=0.3,
                is_similar=False,
                threshold_used=0.7
            )
        ]
        
        comparator = RecipeSimilarityComparator(cache_dir=self.temp_dir)
        summary = comparator.get_similarity_summary(results)
        
        self.assertEqual(summary["total_comparisons"], 2)
        self.assertEqual(summary["similar_recipes"], 1)
        self.assertEqual(summary["similarity_rate"], 0.5)
        self.assertEqual(summary["average_similarity_score"], 0.55)


if __name__ == "__main__":
    unittest.main()