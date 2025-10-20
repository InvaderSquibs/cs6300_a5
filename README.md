# Vector Template

A comprehensive template for vector databases with smolagents integration, featuring examples and analytics for both local and hosted solutions. This project provides a complete framework for building vector database applications with ChromaDB and includes specialized tools for recipe data processing.

## Features

- **ChromaDB Integration**: Full-featured vector database operations with local and server modes
- **Smolagents Support**: AI agent integration for intelligent vector database interactions  
- **FastAPI Server**: RESTful API for vector database operations
- **Recipe Specialization**: Built-in tools for processing and searching recipe data from Kaggle datasets
- **CLI Interface**: Command-line tools for easy database management
- **Comprehensive Testing**: Unit and integration tests included

## Quick Start

The Vector Template can be explored even without installing heavy dependencies. The core data processing utilities work with just Python's standard library.

### No Dependencies Demo

```bash
# Clone the repository
git clone https://github.com/InvaderSquibs/vector_template.git
cd vector_template

# Run the demo (works without external dependencies)
python demo.py

# Test the structure
python test_structure.py
```

### Full Installation

```bash
# Clone the repository
git clone https://github.com/InvaderSquibs/vector_template.git
cd vector_template

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev]"
```

### Basic Usage

#### 1. Quick Demo (No Dependencies Required)

```bash
# See what the project can do without installing heavy dependencies
python demo.py

# Test the project structure
python test_structure.py
```

#### 2. Run the Recipe Example

```bash
# Run basic example with sample recipes
python cli.py example

# Or run with your own CSV file
python cli.py example --csv-file /path/to/recipes.csv
```

#### 3. Start the API Server

```bash
# Start the FastAPI server
python cli.py serve --host 0.0.0.0 --port 8000

# With auto-reload for development
python cli.py serve --reload
```

#### 4. Interactive Mode

```bash
# Start interactive CLI
python cli.py interactive
```

#### 5. Automated Setup

```bash
# Run the setup script (installs dependencies and runs tests)
python setup.py
```

## API Usage

### Starting the Server

```python
from vector_template.api.server import create_app
import uvicorn

app = create_app(
    persist_directory="./my_vector_db",
    collection_name="my_collection"
)

uvicorn.run(app, host="0.0.0.0", port=8000)
```

### API Endpoints

- `POST /documents/add` - Add documents to the vector database
- `POST /documents/query` - Search for similar documents
- `DELETE /documents/delete` - Delete documents by ID
- `PUT /documents/update` - Update existing documents
- `GET /collections/info` - Get collection information
- `GET /collections/list` - List all collections
- `POST /collections/create` - Create a new collection
- `POST /agent/task` - Run smolagents tasks
- `POST /recipes/add` - Add recipes with specialized processing

### Example API Usage

```python
import httpx

# Add documents
response = httpx.post("http://localhost:8000/documents/add", json={
    "documents": ["Recipe for pasta carbonara with eggs and cheese"],
    "metadatas": [{"cuisine": "Italian", "type": "recipe"}],
    "ids": ["pasta_carbonara"]
})

# Search for similar documents
response = httpx.post("http://localhost:8000/documents/query", json={
    "query_texts": "Italian pasta recipes",
    "n_results": 5
})
```

## Programming Usage

### Basic Vector Database Operations

```python
from vector_template.database.chroma_client import ChromaVectorDB

# Initialize database
db = ChromaVectorDB(
    persist_directory="./chroma_db",
    collection_name="recipes"
)

# Add documents
db.add_documents(
    documents=["Pasta carbonara recipe with eggs and cheese"],
    metadatas=[{"cuisine": "Italian"}],
    ids=["carbonara_1"]
)

# Search for similar documents
results = db.query("Italian pasta dishes", n_results=5)
print(results)
```

### Using Smolagents

```python
from vector_template.agents.smol_agent import SmolVectorAgent

# Initialize agent
agent = SmolVectorAgent(
    persist_directory="./chroma_db",
    collection_name="recipes"
)

# Run agent tasks
result = agent.run("Find me pasta recipes with cheese")
print(result)

# Add recipes using specialized method
recipes = [
    {
        "name": "Spaghetti Carbonara",
        "ingredients": ["spaghetti", "eggs", "cheese", "pancetta"],
        "instructions": "Cook pasta, mix with eggs and cheese...",
        "cuisine": "Italian"
    }
]
agent.add_recipe_documents(recipes)
```

### Recipe Data Processing

```python
from vector_template.utils.data_processing import (
    load_recipes_from_csv,
    preprocess_recipe_text,
    extract_recipe_metadata
)

# Load recipes from Kaggle CSV format
recipes = load_recipes_from_csv("foodcom_recipes.csv")

# Process individual recipe
recipe_text = preprocess_recipe_text(recipes[0])
metadata = extract_recipe_metadata(recipes[0])

print(f"Processed text: {recipe_text}")
print(f"Metadata: {metadata}")
```

## Configuration

### Environment Variables

- `CHROMA_HOST`: Chroma server host (for client-server mode)
- `CHROMA_PORT`: Chroma server port (for client-server mode)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Database Modes

#### Local Persistent Mode (Default)
```python
db = ChromaVectorDB(persist_directory="./chroma_db")
```

#### Client-Server Mode
```python
db = ChromaVectorDB(host="localhost", port=8000)
```

## Recipe Dataset Integration

This template is designed to work with the FoodCom recipes dataset from Kaggle:
https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews

### Expected CSV Format

```csv
name,ingredients,directions,description,prep_time,cook_time,servings
"Pasta Carbonara","['spaghetti', 'eggs', 'cheese']","Cook pasta then mix with eggs","Traditional Italian dish",10,15,4
```

### Loading Recipe Data

```python
from vector_template.examples.recipe_example import RecipeVectorExample

# Initialize example with recipe data
example = RecipeVectorExample()

# Load from CSV file
example.load_and_process_csv_file("path/to/foodcom_recipes.csv")

# Search recipes
example.search_recipes("Italian pasta", n_results=5)
```

## CLI Commands

```bash
# Show help
python cli.py --help

# Start API server
python cli.py serve --host 0.0.0.0 --port 8000

# Run examples
python cli.py example
python cli.py example --csv-file recipes.csv

# Interactive mode
python cli.py interactive

# With custom database path
python cli.py --db-path ./my_db interactive
```

## Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/vector_template

# Run specific test file
pytest tests/unit/test_chroma_client.py -v
```

## Architecture

```
vector_template/
├── src/vector_template/
│   ├── database/          # Vector database operations
│   │   └── chroma_client.py
│   ├── agents/            # Smolagents integration
│   │   └── smol_agent.py
│   ├── api/              # FastAPI server
│   │   └── server.py
│   ├── utils/            # Utilities and data processing
│   │   └── data_processing.py
│   └── examples/         # Usage examples
│       └── recipe_example.py
├── tests/                # Test suites
├── cli.py               # Command-line interface
├── requirements.txt     # Dependencies
└── pyproject.toml      # Project configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Add more embedding model options
- [ ] Implement hybrid search (vector + keyword)
- [ ] Add batch processing capabilities
- [ ] Create web UI for vector database management
- [ ] Add more specialized data processors
- [ ] Implement query result caching
- [ ] Add monitoring and analytics dashboard
