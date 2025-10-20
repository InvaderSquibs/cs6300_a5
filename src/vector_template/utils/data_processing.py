"""Utility functions for data processing and management."""

from typing import Any, Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

try:
    import pandas as pd
except ImportError:
    pd = None


def load_recipes_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Load recipes from a CSV file.
    
    Expected columns for FoodCom dataset:
    - name: Recipe name
    - ingredients: Recipe ingredients (as string or list)
    - directions: Cooking instructions
    - description: Recipe description
    - prep_time: Preparation time
    - cook_time: Cooking time
    - servings: Number of servings
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of recipe dictionaries
    """
    if pd is None:
        raise ImportError("pandas is required for CSV loading. Install it with: pip install pandas")
    
    try:
        df = pd.read_csv(file_path)
        recipes = []
        
        for index, row in df.iterrows():
            recipe = {
                "id": f"recipe_{index}",
                "name": row.get("name", "Unknown Recipe"),
                "description": row.get("description", ""),
                "prep_time": row.get("prep_time"),
                "cook_time": row.get("cook_time"),
                "servings": row.get("servings"),
            }
            
            # Handle ingredients - could be string or list
            ingredients = row.get("ingredients", "")
            if isinstance(ingredients, str):
                # Assume comma-separated or other common format
                if ingredients.startswith("[") and ingredients.endswith("]"):
                    # JSON-like format
                    try:
                        recipe["ingredients"] = json.loads(ingredients.replace("'", '"'))
                    except:
                        recipe["ingredients"] = [ing.strip() for ing in ingredients.strip("[]").split(",")]
                else:
                    # Comma-separated
                    recipe["ingredients"] = [ing.strip() for ing in ingredients.split(",") if ing.strip()]
            elif isinstance(ingredients, list):
                recipe["ingredients"] = ingredients
            else:
                recipe["ingredients"] = []
            
            # Handle directions/instructions
            instructions = row.get("directions", row.get("instructions", ""))
            recipe["instructions"] = instructions
            
            # Add any additional columns as metadata
            for col in df.columns:
                if col not in ["name", "ingredients", "directions", "instructions", "description", "prep_time", "cook_time", "servings"]:
                    recipe[col] = row.get(col)
            
            recipes.append(recipe)
        
        logger.info(f"Loaded {len(recipes)} recipes from {file_path}")
        return recipes
    
    except Exception as e:
        logger.error(f"Error loading recipes from CSV: {str(e)}")
        raise


def load_recipes_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load recipes from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of recipe dictionaries
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            recipes = data
        elif isinstance(data, dict) and "recipes" in data:
            recipes = data["recipes"]
        else:
            recipes = [data]
        
        # Ensure each recipe has an ID
        for i, recipe in enumerate(recipes):
            if "id" not in recipe:
                recipe["id"] = f"recipe_{i}"
        
        logger.info(f"Loaded {len(recipes)} recipes from {file_path}")
        return recipes
    
    except Exception as e:
        logger.error(f"Error loading recipes from JSON: {str(e)}")
        raise


def preprocess_recipe_text(recipe: Dict[str, Any]) -> str:
    """
    Preprocess a recipe dictionary into a searchable text format.
    
    Args:
        recipe: Recipe dictionary
        
    Returns:
        Preprocessed text string
    """
    text_parts = []
    
    # Add recipe name
    if "name" in recipe:
        text_parts.append(f"Recipe: {recipe['name']}")
    
    # Add description
    if "description" in recipe and recipe["description"]:
        text_parts.append(f"Description: {recipe['description']}")
    
    # Add ingredients
    if "ingredients" in recipe and recipe["ingredients"]:
        if isinstance(recipe["ingredients"], list):
            ingredients_text = ", ".join(recipe["ingredients"])
        else:
            ingredients_text = str(recipe["ingredients"])
        text_parts.append(f"Ingredients: {ingredients_text}")
    
    # Add instructions
    if "instructions" in recipe and recipe["instructions"]:
        text_parts.append(f"Instructions: {recipe['instructions']}")
    
    # Add cooking details
    cooking_details = []
    if "prep_time" in recipe and recipe["prep_time"]:
        cooking_details.append(f"Prep time: {recipe['prep_time']}")
    if "cook_time" in recipe and recipe["cook_time"]:
        cooking_details.append(f"Cook time: {recipe['cook_time']}")
    if "servings" in recipe and recipe["servings"]:
        cooking_details.append(f"Servings: {recipe['servings']}")
    
    if cooking_details:
        text_parts.append(f"Details: {', '.join(cooking_details)}")
    
    return "\\n".join(text_parts)


def extract_recipe_metadata(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a recipe dictionary.
    
    Args:
        recipe: Recipe dictionary
        
    Returns:
        Metadata dictionary
    """
    metadata = {
        "type": "recipe",
        "name": recipe.get("name", "Unknown"),
    }
    
    # Add standard fields
    for field in ["cuisine", "prep_time", "cook_time", "servings", "difficulty", "category"]:
        if field in recipe and recipe[field] is not None:
            metadata[field] = recipe[field]
    
    # Add ingredient count
    if "ingredients" in recipe and recipe["ingredients"]:
        if isinstance(recipe["ingredients"], list):
            metadata["ingredient_count"] = len(recipe["ingredients"])
        else:
            metadata["ingredient_count"] = len(str(recipe["ingredients"]).split(","))
    
    return metadata


def chunk_large_recipe(recipe: Dict[str, Any], max_chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """
    Split a large recipe into smaller chunks for better vector search.
    
    Args:
        recipe: Recipe dictionary
        max_chunk_size: Maximum size of each chunk in characters
        
    Returns:
        List of recipe chunks
    """
    chunks = []
    base_metadata = extract_recipe_metadata(recipe)
    
    # Create main recipe chunk
    main_text = preprocess_recipe_text(recipe)
    if len(main_text) <= max_chunk_size:
        return [{
            "text": main_text,
            "metadata": base_metadata,
            "id": recipe.get("id", "unknown")
        }]
    
    # Split into components
    components = [
        ("name_description", f"Recipe: {recipe.get('name', 'Unknown')}\\nDescription: {recipe.get('description', '')}"),
        ("ingredients", f"Ingredients: {', '.join(recipe.get('ingredients', [])) if isinstance(recipe.get('ingredients'), list) else recipe.get('ingredients', '')}"),
        ("instructions", f"Instructions: {recipe.get('instructions', '')}"),
    ]
    
    chunk_id = 0
    for component_type, text in components:
        if not text.strip():
            continue
        
        # Further split if still too large
        if len(text) <= max_chunk_size:
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_type"] = component_type
            chunks.append({
                "text": text,
                "metadata": chunk_metadata,
                "id": f"{recipe.get('id', 'unknown')}_chunk_{chunk_id}"
            })
            chunk_id += 1
        else:
            # Split into smaller pieces
            words = text.split()
            current_chunk = []
            current_size = 0
            
            for word in words:
                if current_size + len(word) + 1 > max_chunk_size and current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata["chunk_type"] = component_type
                    chunks.append({
                        "text": chunk_text,
                        "metadata": chunk_metadata,
                        "id": f"{recipe.get('id', 'unknown')}_chunk_{chunk_id}"
                    })
                    chunk_id += 1
                    current_chunk = [word]
                    current_size = len(word)
                else:
                    current_chunk.append(word)
                    current_size += len(word) + 1
            
            # Add remaining words
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunk_metadata = base_metadata.copy()
                chunk_metadata["chunk_type"] = component_type
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata,
                    "id": f"{recipe.get('id', 'unknown')}_chunk_{chunk_id}"
                })
                chunk_id += 1
    
    return chunks


def format_search_results(results: Dict[str, Any], max_results: int = 10) -> str:
    """
    Format search results for display.
    
    Args:
        results: Search results from ChromaDB
        max_results: Maximum number of results to format
        
    Returns:
        Formatted results string
    """
    if not results.get("documents") or not results["documents"][0]:
        return "No results found."
    
    formatted = []
    documents = results["documents"][0][:max_results]
    metadatas = results.get("metadatas", [[]])[0][:max_results]
    distances = results.get("distances", [[]])[0][:max_results]
    ids = results.get("ids", [[]])[0][:max_results]
    
    for i, doc in enumerate(documents):
        metadata = metadatas[i] if i < len(metadatas) else {}
        distance = distances[i] if i < len(distances) else "N/A"
        doc_id = ids[i] if i < len(ids) else "N/A"
        
        # Extract recipe name from metadata if available
        recipe_name = metadata.get("name", "Unknown Recipe")
        
        formatted.append(
            f"\\n{'='*50}\\n"
            f"Result {i+1}: {recipe_name}\\n"
            f"ID: {doc_id}\\n"
            f"Similarity Score: {1-float(distance):.4f}\\n"
            f"{'='*50}\\n"
            f"{doc}\\n"
        )
    
    return "\\n".join(formatted)