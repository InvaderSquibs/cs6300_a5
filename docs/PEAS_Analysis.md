# PEAS Analysis - ArXiv RAG Pipeline

**Project:** CS6300 Assignment 5 - ArXiv RAG Pipeline  
**Date:** October 2024  
**Framework:** PEAS (Performance, Environment, Actuators, Sensors)

## Performance Measure

- Successfully fetching academic papers from arXiv API
- Correctly populating ChromaDB with paper embeddings
- Accurate context retrieval for user queries
- Natural conversational responses using retrieved context
- End-to-end success: user query → retrieval → LLM response

## Tool-Level Success Metrics

- **ArXiv Fetching**: 12+ papers retrieved with abstracts and full text
- **Vector DB Population**: All papers encoded and stored with metadata
- **RAG Retrieval**: Top-5 relevant papers retrieved for each query
- **Chat Management**: Conversation history maintained across sessions

## Environment

- ArXiv API for academic paper discovery
- ChromaDB vector database for paper storage
- LM Studio local LLM server
- User research questions and meeting preparation needs
- Local file system for chat history and reports

## Actuators (Tools)

1. **ArXiv Fetcher** - Searches and retrieves papers with PDF parsing
2. **Vector DB Populator** - Encodes and stores papers in ChromaDB
3. **RAG Engine** - Retrieves relevant context and manages caching
4. **Chat Manager** - Maintains conversation history and sessions

## Sensors

- ArXiv API responses for paper metadata
- PDF parsing for full paper text
- Sentence transformers for text embeddings
- LLM responses via LM Studio API
- File system for chat history persistence

## Environment Properties Analysis

### Observable vs. Partially Observable

**Partially Observable** - The agent cannot observe:
- All available papers on arXiv (only retrieves top results)
- User's actual meeting context or specific research needs
- Complete paper content (some PDFs may be inaccessible)
- Future paper releases or arXiv updates

**Fully Observable** - The agent has complete observability of:
- Retrieved paper abstracts and full text content
- Vector database contents and similarity scores
- Conversation history and chat sessions
- Local file system for data storage
- All tool inputs and outputs during execution

### Deterministic vs. Stochastic

**Stochastic** - The environment exhibits randomness:
- LLM responses vary for the same input (temperature settings)
- ArXiv search results can vary based on timing and indexing
- Paper availability may change (withdrawn papers, access issues)
- Vector similarity scores can vary slightly between runs

**Deterministic** - Some aspects are predictable:
- ArXiv API responses for the same query
- Vector encoding and storage operations
- File system operations for chat history
- Tool execution follows consistent logic

### Episodic vs. Sequential

**Sequential** - The environment has strong temporal dependencies:
- Tools build on each other (fetch → populate → retrieve → respond)
- Each tool's output becomes the next tool's input
- Conversation history influences future responses
- Context retrieval depends on previous database population
- Chat sessions maintain state across multiple interactions
- RAG retrieval quality improves with more papers in database

### Static vs. Dynamic

**Dynamic** - The environment changes over time:
- New papers are constantly added to arXiv
- User research interests and questions evolve
- Vector database grows with new paper additions
- Conversation context accumulates over time

**Static** - Some aspects remain constant:
- ArXiv API interface and response format
- ChromaDB storage structure and operations
- Tool interfaces and capabilities
- Local file system structure

### Discrete vs. Continuous

**Discrete** - All actions and states are discrete:
- Tool calls are discrete actions
- Paper retrieval and processing are discrete operations
- Success/failure states are binary
- Conversation turns are discrete interactions
- Vector similarity scores are discrete values
- Chat sessions are discrete entities

---

*This analysis provides the foundation for understanding the ArXiv RAG Pipeline's design decisions and operational characteristics.*
