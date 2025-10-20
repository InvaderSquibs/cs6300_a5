# Tool Specifications - ArXiv RAG Pipeline

**Project:** CS6300 Assignment 5 - ArXiv RAG Pipeline  
**Date:** October 2024  
**Framework:** 4 Specialized Tools for RAG Pipeline

## Tool 1: ArXiv Fetcher

**Name:** `arxiv_fetcher`

**Description:** 
Searches arXiv API for academic papers on specified topics, parses Atom XML responses, and extracts full paper content including abstracts and PDF text. Handles pagination and rate limiting while providing structured paper data for vector database population.

**Inputs:**
- `topic` (string): Research topic to search for (e.g., 'neural networks', 'machine learning')
- `max_papers` (int, optional): Maximum number of papers to retrieve (default: 12)

**Outputs:**
- List of dictionaries containing:
  - `id` (string): ArXiv paper ID
  - `title` (string): Paper title
  - `abstract` (string): Paper abstract
  - `authors` (string): Comma-separated author list
  - `categories` (string): Comma-separated category list
  - `text` (string): Combined abstract and full PDF text
  - `pdf_url` (string): Direct PDF download URL
  - `published` (string): Publication date
  - `source` (string): Always "arxiv"

**Error Handling:**
- **API Errors**: ArXiv API unavailability, rate limiting, malformed responses
- **PDF Processing Errors**: PDF download failures, parsing errors, text extraction issues
- **Content Errors**: Empty abstracts, inaccessible PDFs, encoding problems
- **Network Errors**: Connection timeouts, SSL certificate issues, download failures

## Tool 2: Vector DB Populator

**Name:** `vector_db_populator`

**Description:**
Initializes ChromaDB collections, encodes paper text using sentence-transformers, and populates vector database with embeddings and metadata. Supports similarity search with metadata filtering and provides abstraction for different vector database backends.

**Inputs:**
- `texts` (list): List of paper texts to encode and store
- `metadata` (list): List of metadata dictionaries for each paper
- `collection_name` (string): Name for the ChromaDB collection

**Outputs:**
- Boolean success indicator
- Collection statistics (number of documents added)
- Encoder initialization confirmation

**Error Handling:**
- **Database Errors**: ChromaDB connection failures, collection creation errors
- **Encoding Errors**: Sentence transformer failures, text preprocessing issues
- **Metadata Errors**: Invalid metadata format, type conversion failures
- **Storage Errors**: Disk space issues, permission problems, corruption

## Tool 3: RAG Engine

**Name:** `rag_engine`

**Description:**
Retrieves top-k relevant papers for user queries, implements context caching for performance, builds prompts with retrieved context and conversation history, and manages context window to prevent LLM overflow. Provides intelligent truncation and dynamic prompt sizing.

**Inputs:**
- `user_query` (string): User's question or request
- `conversation_history` (list, optional): Previous conversation messages
- `top_k` (int, optional): Number of relevant papers to retrieve (default: 5)

**Outputs:**
- Tuple containing:
  - `response` (string): LLM-generated response with context
  - `retrieved_context` (list): Retrieved papers with similarity scores
  - Context truncation warnings if needed

**Error Handling:**
- **Retrieval Errors**: Vector database failures, similarity search errors
- **Context Errors**: Context window overflow, prompt truncation issues
- **LLM Errors**: API failures, response parsing errors, timeout issues
- **Cache Errors**: Cache corruption, TTL expiration, memory issues

## Tool 4: Chat Manager

**Name:** `chat_manager`

**Description:**
Creates and manages chat sessions, maintains conversation history across interactions, saves chat sessions to JSON files, and loads previous conversations for context. Provides session persistence and conversation state management.

**Inputs:**
- `session_id` (string, optional): Existing session ID or None for new session
- `topic` (string): Topic for the chat session
- `message` (dict): Message to add with role and content

**Outputs:**
- Session object with:
  - `session_id` (string): Unique session identifier
  - `conversation_history` (list): List of message dictionaries
  - `session_metadata` (dict): Timestamp, topic, message count
  - `file_path` (string): Path to saved session file

**Error Handling:**
- **Session Errors**: Session creation failures, ID conflicts
- **File Errors**: JSON serialization failures, file write errors
- **History Errors**: Message format validation, conversation corruption
- **Storage Errors**: Directory creation failures, permission issues

---

*These four tools work together to create a complete RAG pipeline: ArXiv Fetcher retrieves papers, Vector DB Populator stores them, RAG Engine retrieves relevant context, and Chat Manager maintains conversation state.*
