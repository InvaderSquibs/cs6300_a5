"""Example usage of the vector template with recipe data."""

import asyncio
import logging
from typing import List, Dict, Any
from ..database.chroma_client import ChromaVectorDB
from ..agents.smol_agent import SmolVectorAgent
from ..utils.data_processing import (
    load_recipes_from_csv,
    load_recipes_from_json,
    preprocess_recipe_text,
    extract_recipe_metadata,
    chunk_large_recipe,
    format_search_results,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecipeVectorExample:
    """Example class demonstrating recipe vector database operations."""
    
    def __init__(self, persist_directory: str = "./example_chroma_db"):
        """Initialize the example with a vector database."""
        self.vector_db = ChromaVectorDB(
            persist_directory=persist_directory,
            collection_name="recipe_collection"
        )
        self.smol_agent = SmolVectorAgent(vector_db=self.vector_db)
        logger.info("Initialized RecipeVectorExample")
    
    def add_sample_recipes(self) -> None:
        """Add some sample recipes to demonstrate functionality."""
        sample_recipes = [
            {
                "id": "pasta_carbonara",
                "name": "Classic Pasta Carbonara",
                "description": "A traditional Italian pasta dish with eggs, cheese, and pancetta",
                "ingredients": [
                    "400g spaghetti",
                    "200g pancetta or guanciale",
                    "4 large eggs",
                    "100g Pecorino Romano cheese",
                    "Black pepper",
                    "Salt"
                ],
                "instructions": "1. Cook pasta in salted water. 2. Fry pancetta until crispy. 3. Mix eggs and cheese. 4. Combine hot pasta with pancetta, then add egg mixture off heat. 5. Toss quickly and serve.",
                "prep_time": "10 minutes",
                "cook_time": "15 minutes",
                "servings": 4,
                "cuisine": "Italian"
            },
            {
                "id": "chicken_curry",
                "name": "Spicy Chicken Curry",
                "description": "A flavorful and aromatic chicken curry with Indian spices",
                "ingredients": [
                    "500g chicken breast",
                    "2 onions",
                    "3 cloves garlic",
                    "1 inch ginger",
                    "2 tsp curry powder",
                    "1 tsp turmeric",
                    "400ml coconut milk",
                    "2 tbsp vegetable oil",
                    "Salt to taste"
                ],
                "instructions": "1. Cut chicken into pieces. 2. Sauté onions, garlic, and ginger. 3. Add spices and cook for 1 minute. 4. Add chicken and brown. 5. Pour in coconut milk and simmer for 20 minutes.",
                "prep_time": "15 minutes",
                "cook_time": "25 minutes",
                "servings": 4,
                "cuisine": "Indian"
            },
            {
                "id": "chocolate_cake",
                "name": "Rich Chocolate Cake",
                "description": "Moist and decadent chocolate cake perfect for special occasions",
                "ingredients": [
                    "200g dark chocolate",
                    "200g butter",
                    "200g sugar",
                    "4 eggs",
                    "100g flour",
                    "50g cocoa powder",
                    "1 tsp baking powder",
                    "Pinch of salt"
                ],
                "instructions": "1. Preheat oven to 180°C. 2. Melt chocolate and butter. 3. Beat eggs and sugar until fluffy. 4. Combine all ingredients. 5. Bake for 25-30 minutes.",
                "prep_time": "20 minutes",
                "cook_time": "30 minutes",
                "servings": 8,
                "cuisine": "International"
            }
        ]
        
        # Process and add recipes
        documents = []
        metadatas = []
        ids = []
        
        for recipe in sample_recipes:
            doc_text = preprocess_recipe_text(recipe)
            metadata = extract_recipe_metadata(recipe)
            
            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(recipe["id"])
        
        self.vector_db.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(sample_recipes)} sample recipes")
    
    def search_recipes(self, query: str, n_results: int = 3) -> None:
        """Search for recipes and display results."""
        logger.info(f"Searching for: '{query}'")
        
        results = self.vector_db.query(
            query_texts=query,
            n_results=n_results
        )
        
        formatted_results = format_search_results(results, max_results=n_results)
        print(f"\\nSearch Results for '{query}':")
        print(formatted_results)
    
    def demonstrate_agent_capabilities(self) -> None:
        """Demonstrate the smolagents integration."""
        logger.info("Demonstrating agent capabilities")
        
        # Example tasks for the agent
        tasks = [
            "Show me information about the current collection",
            "Search for pasta recipes",
            "Find recipes with chocolate",
            "Look for quick recipes with prep time under 20 minutes"
        ]
        
        for task in tasks:
            print(f"\\n{'='*60}")
            print(f"Agent Task: {task}")
            print('='*60)
            
            try:
                result = self.smol_agent.run(task)
                print(result)
            except Exception as e:
                print(f"Error running task: {e}")
    
    def load_and_process_csv_file(self, file_path: str) -> None:
        """Load recipes from a CSV file and add them to the database."""
        try:
            recipes = load_recipes_from_csv(file_path)
            result = self.smol_agent.add_recipe_documents(recipes)
            logger.info(result)
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
    
    def run_complete_example(self) -> None:
        """Run a complete example demonstrating all features."""
        print("\\n" + "="*80)
        print("VECTOR TEMPLATE RECIPE EXAMPLE")
        print("="*80)
        
        # 1. Add sample recipes
        print("\\n1. Adding sample recipes...")
        self.add_sample_recipes()
        
        # 2. Show collection info
        info = self.vector_db.get_collection_info()
        print(f"\\n2. Collection Info: {info}")
        
        # 3. Perform various searches
        print("\\n3. Performing recipe searches...")
        search_queries = [
            "Italian pasta dishes",
            "spicy curry recipes",
            "chocolate desserts",
            "quick and easy meals",
            "recipes with chicken"
        ]
        
        for query in search_queries:
            self.search_recipes(query, n_results=2)
        
        # 4. Demonstrate agent capabilities
        print("\\n4. Demonstrating Agent Capabilities...")
        self.demonstrate_agent_capabilities()
        
        print("\\n" + "="*80)
        print("EXAMPLE COMPLETED")
        print("="*80)


def run_example():
    """Run the example."""
    example = RecipeVectorExample()
    example.run_complete_example()


def run_csv_example(csv_file_path: str):
    """Run example with CSV file."""
    example = RecipeVectorExample()
    example.load_and_process_csv_file(csv_file_path)
    
    # Perform some searches on the loaded data
    search_queries = ["breakfast recipes", "vegetarian dishes", "quick meals"]
    for query in search_queries:
        example.search_recipes(query)


if __name__ == "__main__":
    # Run the basic example
    run_example()