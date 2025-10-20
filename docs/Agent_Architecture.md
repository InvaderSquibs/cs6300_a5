# Agent Architecture - ArXiv RAG Pipeline

**Project:** CS6300 Assignment 5 - ArXiv RAG Pipeline  
**Date:** October 2024  
**Framework:** Two-Flow Architecture with Local LLM

## Framework Choice

- **Custom Python Implementation**: Built with smolagents-compatible structure for tool integration
- Provides clean separation between population and conversation phases
- Supports both scripted orchestration and model-driven responses
- Minimal overhead for rapid prototyping and testing

## Model Configuration

- **Model**: `qwen/qwen3-4b-2507` (local deployment via LM Studio)
- **Endpoint**: `http://localhost:1234/v1` (local LLM server)
- **Rationale**: Chosen for cost efficiency, privacy, and rapid iteration without cloud credits
- **API Compatibility**: OpenAI-compatible interface for seamless integration
- **Context Management**: Intelligent truncation and dynamic prompt sizing

## Two-Flow Architecture

### Flow 1: Population Pipeline
```
User Topic → ArXiv Fetcher → Papers (title, abstract, PDF text) →
Vector DB Populator → Encode with sentence-transformers →
Store in ChromaDB → Ready for queries
```

### Flow 2: Conversation Pipeline
```
User Question → RAG Engine (retrieve top-k papers) →
Build prompt (context + history) → LLM Studio API →
Response with citations → Chat Manager (save) → Continue conversation
```

## Context Management

- **Intelligent Truncation**: 1000 characters per message limit
- **Reduced Context Window**: 2 messages maximum in conversation history
- **Dynamic Prompt Sizing**: Estimates total prompt length and truncates proactively
- **Overflow Prevention**: Graceful handling of context window overflow errors
- **Cache Management**: Context caching for improved performance

## Orchestration Strategy

- **Sequential Tool Execution**: Tools execute in predetermined order for each flow
- **State Management**: Each tool reads and modifies the current system state
- **Flow Separation**: Population and conversation phases are independent
- **Error Handling**: Failed operations are logged but don't stop the pipeline
- **Session Persistence**: Chat history maintained across interactions

## Tool Integration

- **Modular Design**: Each tool is independently testable and maintainable
- **JSON Communication**: Tools communicate via structured data formats
- **State Passing**: Paper data flows through the pipeline with metadata preservation
- **Error Propagation**: Failed tool calls are handled gracefully with fallback options
- **Unified Test Runner**: Single framework for testing all scenarios

## Key Design Decisions

- **Local LLM**: Chosen for cost efficiency, privacy, and rapid iteration
- **Two-Phase Architecture**: Clear separation between data preparation and usage
- **Context-Aware Responses**: RAG retrieval ensures relevant, cited responses
- **Conversation Continuity**: Chat history enables natural multi-turn interactions
- **Intelligent Caching**: Context caching improves performance and reduces API calls
- **Graceful Degradation**: System continues working even if individual components fail

## Vector Database Integration

The system uses ChromaDB for efficient similarity search:
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 for text encoding
- **Metadata Storage**: Paper titles, authors, categories, and publication dates
- **Similarity Search**: Top-k retrieval based on semantic similarity
- **Collection Management**: Topic-based collections for organized storage

## Output Organization

The system uses an organized folder structure for better project management:
- **`data/vector_db/`**: ChromaDB collections and embeddings
- **`data/chat_history/`**: JSON files for conversation sessions
- **`data/reports/`**: Test results and evaluation metrics
- **`data/models/`**: Downloaded sentence transformer models
- **Source Integration**: All responses include paper citations and source links

---

*This architecture provides a robust foundation for academic paper retrieval and conversational AI, with clear separation of concerns and intelligent context management.*
