"""Data models for recipe similarity evaluation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    """Recipe data model."""
    
    id: str = Field(..., description="Unique identifier for the recipe")
    title: str = Field(..., description="Recipe title")
    ingredients: List[str] = Field(default_factory=list, description="List of ingredients")
    instructions: List[str] = Field(default_factory=list, description="Cooking instructions")
    description: Optional[str] = Field(None, description="Recipe description")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine")
    cooking_time: Optional[int] = Field(None, description="Cooking time in minutes")
    serving_size: Optional[int] = Field(None, description="Number of servings")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    def to_text(self) -> str:
        """Convert recipe to text representation for comparison."""
        text_parts = [
            f"Title: {self.title}",
            f"Description: {self.description or 'No description'}",
            f"Ingredients: {', '.join(self.ingredients)}",
            f"Instructions: {' '.join(self.instructions)}",
        ]
        
        if self.cuisine_type:
            text_parts.append(f"Cuisine: {self.cuisine_type}")
        if self.cooking_time:
            text_parts.append(f"Cooking time: {self.cooking_time} minutes")
        if self.serving_size:
            text_parts.append(f"Serves: {self.serving_size}")
            
        return " | ".join(text_parts)


class SimilarityResult(BaseModel):
    """Result of recipe similarity comparison."""
    
    target_recipe_id: str = Field(..., description="ID of the target recipe being compared")
    candidate_recipe_id: str = Field(..., description="ID of the candidate recipe")
    similarity_score: float = Field(..., description="Similarity score between 0 and 1")
    is_similar: bool = Field(..., description="Boolean indicating if recipes are similar")
    threshold_used: float = Field(..., description="Threshold used for similarity determination")
    

class SummarizationResponse(BaseModel):
    """Response from summarization query containing recipe data."""
    
    target_recipe: Recipe = Field(..., description="The main recipe to compare against")
    candidate_recipes: List[Recipe] = Field(..., description="List of k candidate recipes to compare")
    query_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query metadata")