# Vector Database Template

A comprehensive template for vector databases with examples and analytics for both local and hosted solutions. This template provides a complete implementation for populating vector databases and includes both ChromaDB and FAISS backends.

## Features

- **Multiple Backends**: Support for both ChromaDB (hosted) and FAISS (local) vector databases
- **Text Embedding**: Automatic text-to-vector conversion using sentence transformers
- **REST API**: FastAPI-based server for web integration
- **Flexible Population**: Support for both text-based and pre-computed vector population
- **Search Functionality**: Semantic search with similarity scoring
- **Sample Data**: Built-in sample data for testing and demonstration

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/InvaderSquibs/vector_template.git
cd vector_template
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

#### Command Line Examples

Run examples with different backends:
```bash
# ChromaDB example
python examples.py chromadb

# FAISS example  
python examples.py faiss

# Run both examples
python examples.py
```

#### Python API

```python
from src.vector_db_populator import VectorDBPopulator, create_sample_data

# Initialize populator
populator = VectorDBPopulator(backend_type='chromadb')
populator.initialize_database({'collection_name': 'my_collection'})

# Populate with sample data
texts, metadata = create_sample_data()
populator.populate_from_texts(texts, metadata)

# Search for similar vectors
results = populator.search_similar("machine learning", top_k=3)
```

#### REST API Server

Start the FastAPI server:
```bash
python server.py
```

Then access the API at `http://localhost:8000`:

- `POST /initialize` - Initialize the vector database
- `POST /populate` - Populate with custom texts
- `POST /populate/sample` - Populate with sample data
- `POST /search` - Search for similar vectors
- `GET /health` - Health check

Example API usage:
```bash
# Initialize database
curl -X POST "http://localhost:8000/initialize" \
  -H "Content-Type: application/json" \
  -d '{"backend_type": "chromadb", "collection_name": "test"}'

# Populate with sample data
curl -X POST "http://localhost:8000/populate/sample"

# Search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "top_k": 3}'
```

## Architecture

### Core Components

1. **VectorDBPopulator**: Main class for populating vector databases
2. **VectorDBBackend**: Abstract base class for different database backends
3. **ChromaDBBackend**: Implementation for ChromaDB
4. **FAISSBackend**: Implementation for FAISS
5. **Server**: FastAPI REST API server

### Supported Backends

#### ChromaDB
- Best for: Production deployments, hosted solutions
- Features: Persistent storage, metadata filtering, distributed setup
- Configuration: Collection name, persistence directory

#### FAISS
- Best for: Local development, high-performance search
- Features: In-memory indexing, fast similarity search
- Configuration: Vector dimension, index type

## Configuration

Environment variables can be used to override default settings:

```bash
# ChromaDB settings
export CHROMADB_COLLECTION="my_collection"
export CHROMADB_PERSIST_DIR="./my_chroma_db"

# FAISS settings  
export FAISS_DIMENSION="384"

# Encoder settings
export ENCODER_MODEL="all-MiniLM-L6-v2"

# Server settings
export SERVER_HOST="0.0.0.0"
export SERVER_PORT="8000"
```

## Dependencies

- `numpy`: Numerical computations
- `chromadb`: ChromaDB vector database
- `faiss-cpu`: FAISS similarity search
- `sentence-transformers`: Text embedding models
- `fastapi`: Web API framework
- `uvicorn`: ASGI server
- `python-dotenv`: Environment variable management

## Project Structure

```
vector_template/
├── src/
│   ├── __init__.py
│   ├── vector_db_populator.py  # Main population logic
│   └── config.py               # Configuration management
├── server.py                   # FastAPI server
├── examples.py                 # Usage examples
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## License

This project is open source and available under the MIT License.
