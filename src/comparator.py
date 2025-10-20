"""Main recipe similarity comparison service."""

import logging
from typing import List, Optional, Dict, Any

from .models import Recipe, SimilarityResult, SummarizationResponse
from .evaluator import EvaluationModel


logger = logging.getLogger(__name__)


class RecipeSimilarityComparator:
    """Main service for comparing recipe similarities."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize the recipe similarity comparator.
        
        Args:
            model_name: Name of the sentence transformer model
            cache_dir: Directory to cache model files
            similarity_threshold: Threshold for similarity determination
        """
        self.evaluator = EvaluationModel(
            model_name=model_name,
            cache_dir=cache_dir,
            similarity_threshold=similarity_threshold
        )
        self._model_loaded = False
        
    def initialize(self) -> None:
        """Initialize the comparator by downloading and loading the model."""
        logger.info("Initializing recipe similarity comparator...")
        self.evaluator.download_and_load_model()
        self._model_loaded = True
        logger.info("Comparator initialized successfully")
        
    def compare_recipes(
        self,
        summarization_response: SummarizationResponse
    ) -> List[SimilarityResult]:
        """
        Compare the target recipe against candidate recipes.
        
        Args:
            summarization_response: Response containing target and candidate recipes
            
        Returns:
            List of similarity results for each candidate recipe
        """
        if not self._model_loaded:
            raise ValueError("Comparator not initialized. Call initialize() first.")
            
        logger.info(
            f"Comparing target recipe '{summarization_response.target_recipe.title}' "
            f"against {len(summarization_response.candidate_recipes)} candidate recipes"
        )
        
        results = self.evaluator.calculate_similarity(
            target_recipe=summarization_response.target_recipe,
            candidate_recipes=summarization_response.candidate_recipes
        )
        
        # Log results summary
        similar_count = sum(1 for result in results if result.is_similar)
        logger.info(
            f"Comparison complete: {similar_count}/{len(results)} recipes "
            f"deemed similar (threshold: {self.evaluator.similarity_threshold})"
        )
        
        return results
    
    def compare_single_recipes(
        self,
        target_recipe: Recipe,
        candidate_recipes: List[Recipe]
    ) -> List[SimilarityResult]:
        """
        Compare a target recipe against a list of candidate recipes.
        
        Args:
            target_recipe: The recipe to compare against
            candidate_recipes: List of candidate recipes
            
        Returns:
            List of similarity results
        """
        if not self._model_loaded:
            raise ValueError("Comparator not initialized. Call initialize() first.")
            
        return self.evaluator.calculate_similarity(target_recipe, candidate_recipes)
    
    def set_similarity_threshold(self, threshold: float) -> None:
        """Set the similarity threshold."""
        self.evaluator.set_threshold(threshold)
        
    def get_similarity_summary(
        self,
        results: List[SimilarityResult]
    ) -> Dict[str, Any]:
        """
        Get a summary of similarity results.
        
        Args:
            results: List of similarity results
            
        Returns:
            Summary statistics
        """
        if not results:
            return {"total_comparisons": 0}
            
        similar_count = sum(1 for result in results if result.is_similar)
        similarity_scores = [result.similarity_score for result in results]
        
        return {
            "total_comparisons": len(results),
            "similar_recipes": similar_count,
            "dissimilar_recipes": len(results) - similar_count,
            "similarity_rate": similar_count / len(results),
            "average_similarity_score": sum(similarity_scores) / len(similarity_scores),
            "max_similarity_score": max(similarity_scores),
            "min_similarity_score": min(similarity_scores),
            "threshold_used": results[0].threshold_used if results else None
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return self.evaluator.get_model_info()