"""Evaluation model manager for recipe similarity comparison."""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .models import Recipe, SimilarityResult


logger = logging.getLogger(__name__)


class EvaluationModel:
    """Manages the evaluation model for recipe similarity comparison."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize the evaluation model.
        
        Args:
            model_name: Name of the sentence transformer model to use
            cache_dir: Directory to cache the model files
            similarity_threshold: Threshold for determining if recipes are similar
        """
        self.model_name = model_name
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), "models")
        self.similarity_threshold = similarity_threshold
        self.model: Optional[SentenceTransformer] = None
        
        # Ensure cache directory exists
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
    def download_and_load_model(self) -> None:
        """Download and load the evaluation model."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=self.cache_dir
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
            
    def encode_recipes(self, recipes: List[Recipe]) -> np.ndarray:
        """
        Encode recipes into embeddings.
        
        Args:
            recipes: List of recipes to encode
            
        Returns:
            Array of embeddings for the recipes
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call download_and_load_model() first.")
            
        recipe_texts = [recipe.to_text() for recipe in recipes]
        embeddings = self.model.encode(recipe_texts, convert_to_tensor=False)
        return embeddings
    
    def calculate_similarity(
        self,
        target_recipe: Recipe,
        candidate_recipes: List[Recipe]
    ) -> List[SimilarityResult]:
        """
        Calculate similarity between target recipe and candidate recipes.
        
        Args:
            target_recipe: The recipe to compare against
            candidate_recipes: List of candidate recipes to compare
            
        Returns:
            List of similarity results
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call download_and_load_model() first.")
            
        # Encode all recipes
        all_recipes = [target_recipe] + candidate_recipes
        embeddings = self.encode_recipes(all_recipes)
        
        # Target embedding is the first one
        target_embedding = embeddings[0:1]
        candidate_embeddings = embeddings[1:]
        
        # Calculate cosine similarities
        similarities = cosine_similarity(target_embedding, candidate_embeddings)[0]
        
        # Create results
        results = []
        for i, candidate_recipe in enumerate(candidate_recipes):
            similarity_score = float(similarities[i])
            is_similar = similarity_score >= self.similarity_threshold
            
            result = SimilarityResult(
                target_recipe_id=target_recipe.id,
                candidate_recipe_id=candidate_recipe.id,
                similarity_score=similarity_score,
                is_similar=is_similar,
                threshold_used=self.similarity_threshold
            )
            results.append(result)
            
        return results
    
    def set_threshold(self, threshold: float) -> None:
        """Set the similarity threshold."""
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        self.similarity_threshold = threshold
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if self.model is None:
            return {"model_loaded": False}
            
        return {
            "model_loaded": True,
            "model_name": self.model_name,
            "cache_dir": self.cache_dir,
            "similarity_threshold": self.similarity_threshold,
            "max_sequence_length": getattr(self.model, "max_seq_length", "Unknown")
        }