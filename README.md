# Vector Template

A template for vector databases with examples and analytics for both local and hosted solutions. This repository includes a complete validation script that demonstrates how to integrate a local LLM with a vector database for recipe summarization and retrieval.

## Features

- 🤖 **Local LLM Integration**: Connect to any local LLM API (Ollama, LM Studio, etc.)
- 💾 **Vector Database**: Local ChromaDB for storing and querying embeddings
- 🍳 **Recipe Processing**: Sample recipes with LLM summarization
- 🔍 **Semantic Search**: Query recipes by description or ingredients
- 📊 **Analytics**: Database statistics and query performance

## Quick Start

1. **Setup Environment**:
   ```bash
   ./setup.sh
   ```

2. **Configure LLM Connection**:
   Edit the `.env` file to point to your local LLM:
   ```bash
   # Example for Ollama
   GPT_API=http://localhost:11434/v1/chat/completions
   MODEL_NAME=llama2
   
   # Example for LM Studio
   GPT_API=http://localhost:1234/v1/chat/completions
   MODEL_NAME=your-model-name
   ```

3. **Run Validation Script**:
   ```bash
   python validate_vdb.py
   ```

## Prerequisites

- Python 3.8+
- A running local LLM (see [Local LLM Setup](#local-llm-setup))

## Local LLM Setup

### Option 1: Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# Run the server
ollama serve
```

### Option 2: LM Studio
1. Download [LM Studio](https://lmstudio.ai/)
2. Download a model through the UI
3. Start the local server
4. Note the endpoint URL (usually `http://localhost:1234/v1/chat/completions`)

## Usage

### Basic Validation
Process 3 random recipes and test queries:
```bash
python validate_vdb.py
```

### Advanced Options
```bash
# Process more recipes
python validate_vdb.py --num-recipes 10

# Clear existing database
python validate_vdb.py --clear-db

# Only query existing data (skip LLM processing)
python validate_vdb.py --skip-processing

# Custom database path
python validate_vdb.py --db-path ./my_custom_db
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Recipe Data   │───▶│   Local LLM     │───▶│  Vector DB      │
│   (Samples)     │    │   (Summary)     │    │  (ChromaDB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │ Semantic Search │
                                              │   & Retrieval   │
                                              └─────────────────┘
```

## File Structure

```
vector_template/
├── validate_vdb.py      # Main validation script
├── recipe_data.py       # Sample recipe data
├── llm_client.py        # Local LLM API client
├── vector_db.py         # ChromaDB vector database manager
├── requirements.txt     # Python dependencies
├── setup.sh            # Setup script
├── .env.example        # Environment template
└── README.md           # This file
```

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GPT_API` | Yes | Local LLM endpoint URL | `http://localhost:11434/v1/chat/completions` |
| `MODEL_NAME` | No | Model name to use | `llama2` |
| `API_KEY` | No | API key if required | `your-api-key` |

## Troubleshooting

### Connection Issues
- Ensure your local LLM is running and accessible
- Check the `GPT_API` URL in your `.env` file
- Verify the model name matches your LLM setup

### Permission Errors
- Make sure scripts are executable: `chmod +x setup.sh validate_vdb.py`

### Database Issues
- Clear the database: `python validate_vdb.py --clear-db`
- Check disk space for the database path

## Extending the Template

### Adding New Data Sources
1. Create a new data module similar to `recipe_data.py`
2. Update the validation script to use your data
3. Modify the LLM prompts for your domain

### Custom Vector Database
1. Implement your database backend in a new module
2. Follow the interface patterns in `vector_db.py`
3. Update the validation script to use your implementation

### Different LLM Providers
1. Extend `llm_client.py` to support your provider's API
2. Add any required authentication or formatting
3. Test with the validation script

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the validation script
5. Submit a pull request

## License

This project is open source and available under the MIT License.
