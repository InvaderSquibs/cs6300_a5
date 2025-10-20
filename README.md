# Recipe Similarity Evaluation System

A template for vector databases with a complete recipe similarity evaluation system that uses machine learning models to compare recipes and determine similarity based on ingredients, instructions, and metadata.

## Overview

This system takes responses from summarization queries containing recipe data and compares a target recipe against k candidate recipes using a locally downloaded evaluation model. For each comparison, it returns a True/False similarity determination along with confidence scores.

## Features

- **Local Model Execution**: Downloads and runs sentence transformer models locally
- **Recipe Comparison**: Compares recipes based on ingredients, instructions, cuisine type, and metadata
- **Configurable Thresholds**: Adjustable similarity thresholds for different use cases
- **Comprehensive Results**: Provides similarity scores, boolean decisions, and summary statistics
- **JSON Support**: Import/export recipe data and results in JSON format
- **Extensible Design**: Easy to customize for different types of food content

## Installation

1. Clone the repository:
```bash
git clone https://github.com/InvaderSquibs/vector_template.git
cd vector_template
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.models import Recipe, SummarizationResponse
from src.comparator import RecipeSimilarityComparator

# Initialize the comparator
comparator = RecipeSimilarityComparator(
    model_name="all-MiniLM-L6-v2",
    similarity_threshold=0.7
)

# Download and load the model
comparator.initialize()

# Create recipe data
target_recipe = Recipe(
    id="target_001",
    title="Chicken Parmesan",
    ingredients=["chicken", "breadcrumbs", "cheese", "tomato sauce"],
    instructions=["Bread chicken", "Fry until golden", "Add sauce and cheese"]
)

candidate_recipes = [
    Recipe(
        id="candidate_001", 
        title="Chicken Parmigiana",
        ingredients=["chicken cutlets", "breadcrumbs", "parmesan", "marinara"],
        instructions=["Bread cutlets", "Cook until crispy", "Top with sauce"]
    )
]

# Perform comparison
response = SummarizationResponse(
    target_recipe=target_recipe,
    candidate_recipes=candidate_recipes
)

results = comparator.compare_recipes(response)

# Check results
for result in results:
    print(f"Recipe {result.candidate_recipe_id}: {result.is_similar} (score: {result.similarity_score:.3f})")
```

### Run the Demo

```bash
python main.py
```

This will run a demonstration with sample recipes and show the complete evaluation process.

### Using JSON Data

```python
from src.utils import load_recipes_from_json, save_results_to_json

# Load recipes from JSON file
response = load_recipes_from_json("sample_recipes.json")

# Run comparison
results = comparator.compare_recipes(response)

# Save results
save_results_to_json(
    results, 
    response.target_recipe, 
    response.candidate_recipes,
    "similarity_results.json"
)
```

## Configuration

### Model Options

The system supports different sentence transformer models:

- `all-MiniLM-L6-v2` (default): Lightweight and fast
- `all-mpnet-base-v2`: More accurate but larger
- `all-distilroberta-v1`: Good balance of speed and accuracy

### Similarity Threshold

Adjust the similarity threshold based on your needs:
- `0.5`: Very lenient (more recipes considered similar)
- `0.7`: Balanced (default)
- `0.9`: Very strict (only very similar recipes match)

## API Reference

### Core Classes

#### `Recipe`
Represents a recipe with ingredients, instructions, and metadata.

```python
recipe = Recipe(
    id="unique_id",
    title="Recipe Title",
    ingredients=["ingredient1", "ingredient2"],
    instructions=["step1", "step2"],
    description="Recipe description",
    cuisine_type="Italian",
    cooking_time=30,
    serving_size=4
)
```

#### `RecipeSimilarityComparator`
Main service for comparing recipe similarities.

```python
comparator = RecipeSimilarityComparator(
    model_name="all-MiniLM-L6-v2",
    similarity_threshold=0.7
)
```

#### `SimilarityResult`
Result of a recipe comparison containing score and boolean decision.

```python
result = SimilarityResult(
    target_recipe_id="target_001",
    candidate_recipe_id="candidate_001", 
    similarity_score=0.85,
    is_similar=True,
    threshold_used=0.7
)
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Or run individual test files:

```bash
python tests/test_recipe_similarity.py
```

## File Structure

```
vector_template/
├── src/
│   ├── __init__.py
│   ├── models.py          # Data models for recipes and results
│   ├── evaluator.py       # Evaluation model management
│   ├── comparator.py      # Main comparison service
│   └── utils.py           # JSON utilities and helpers
├── config/
│   └── config.py          # Configuration settings
├── tests/
│   └── test_recipe_similarity.py  # Test suite
├── main.py                # Demo script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Example Output

```
RECIPE SIMILARITY EVALUATION RESULTS
============================================================

Target Recipe: Classic Chicken Parmesan
Description: Crispy breaded chicken topped with marinara sauce and melted cheese

Comparison Results (Threshold: 0.7):
--------------------------------------------------

Chicken Parmigiana
  Similarity Score: 0.892
  Status: ✓ SIMILAR
  Description: Breaded chicken cutlets with tomato sauce and cheese

Beef Stir Fry  
  Similarity Score: 0.234
  Status: ✗ NOT SIMILAR
  Description: Quick beef stir fry with vegetables

--------------------------------------------------
SUMMARY:
  Total Comparisons: 2
  Similar Recipes: 1
  Similarity Rate: 50.0%
  Average Score: 0.563
```

## Advanced Usage

### Custom Model Training

You can extend the system to use custom models:

```python
from sentence_transformers import SentenceTransformer

# Train custom model (example)
model = SentenceTransformer('all-MiniLM-L6-v2')
# ... training code ...

# Use custom model
comparator = RecipeSimilarityComparator(model_name="path/to/custom/model")
```

### Batch Processing

For processing large numbers of recipes:

```python
import glob
from src.utils import load_recipes_from_json

# Process multiple files
for json_file in glob.glob("data/*.json"):
    response = load_recipes_from_json(json_file)
    results = comparator.compare_recipes(response)
    # Process results...
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## License

This project is licensed under the MIT License.
