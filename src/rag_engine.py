"""
RAG Engine for Context Retrieval and Caching

This module provides functionality to retrieve relevant context from vector databases,
implement caching for performance, and build prompts for LLM interactions.
"""

import hashlib
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from vector_db_populator import VectorDBPopulator
from llm_client import LLMClient

# Set up logging
logger = logging.getLogger(__name__)


class ContextCache:
    """Simple in-memory cache for RAG context retrieval."""
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 50):
        """
        Initialize the context cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            max_size: Maximum number of cache entries
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: Dict[str, Tuple[List[Dict[str, Any]], datetime]] = {}
    
    def _generate_key(self, query: str, top_k: int) -> str:
        """Generate cache key for query and parameters."""
        key_string = f"{query}:{top_k}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, query: str, top_k: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached results for a query.
        
        Args:
            query: Search query
            top_k: Number of results to retrieve
            
        Returns:
            Cached results or None if not found/expired
        """
        key = self._generate_key(query, top_k)
        
        if key not in self.cache:
            return None
        
        results, timestamp = self.cache[key]
        
        # Check if expired
        if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit for query: {query[:50]}...")
        return results
    
    def set(self, query: str, top_k: int, results: List[Dict[str, Any]]) -> None:
        """
        Cache results for a query.
        
        Args:
            query: Search query
            top_k: Number of results
            results: Results to cache
        """
        key = self._generate_key(query, top_k)
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (results, datetime.now())
        logger.debug(f"Cached results for query: {query[:50]}...")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Context cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }


class RAGEngine:
    """Main RAG engine for context retrieval and prompt building."""
    
    def __init__(
        self, 
        vector_db: VectorDBPopulator,
        llm_client: LLMClient,
        top_k: int = 5,
        context_window: int = 2,
        cache_ttl: int = 300,
        max_cache_size: int = 50
    ):
        """
        Initialize the RAG engine.
        
        Args:
            vector_db: Vector database populator
            llm_client: LLM client for generation
            top_k: Number of top results to retrieve
            context_window: Number of recent messages to include in context
            cache_ttl: Cache time-to-live in seconds
            max_cache_size: Maximum cache size
        """
        self.vector_db = vector_db
        self.llm_client = llm_client
        self.top_k = top_k
        self.context_window = context_window
        self.cache = ContextCache(ttl_seconds=cache_ttl, max_size=max_cache_size)
    
    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from the vector database.
        
        Args:
            query: Search query
            top_k: Number of results to retrieve (uses instance default if None)
            
        Returns:
            List of relevant context documents
        """
        if top_k is None:
            top_k = self.top_k
        
        # Check cache first
        cached_results = self.cache.get(query, top_k)
        if cached_results is not None:
            return cached_results
        
        # Retrieve from vector database
        logger.info(f"Retrieving context for query: {query[:100]}...")
        results = self.vector_db.search_similar(query, top_k=top_k)
        
        # Cache the results
        self.cache.set(query, top_k, results)
        
        return results
    
    def build_rag_prompt(
        self, 
        user_query: str, 
        retrieved_context: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Build a RAG prompt with retrieved context and conversation history.
        
        Args:
            user_query: Current user query
            retrieved_context: Retrieved context documents
            conversation_history: Previous conversation messages
            
        Returns:
            Formatted prompt for LLM
        """
        # Build context section
        context_section = self._format_context(retrieved_context)
        
        # Build conversation history section with intelligent truncation
        history_section = self._format_conversation_history(conversation_history)
        
        # Estimate total prompt length and truncate if necessary
        estimated_length = len(user_query) + len(context_section) + len(history_section) + 500  # 500 for system prompt
        
        # If estimated length is too long, reduce context
        if estimated_length > 3000:  # Conservative limit
            logger.warning(f"Prompt too long ({estimated_length} chars), reducing context")
            # Truncate context section
            if len(context_section) > 1500:
                context_section = context_section[:1500] + "\n... [context truncated]"
            # Truncate history section more aggressively
            if len(history_section) > 1000:
                history_section = history_section[:1000] + "\n... [history truncated]"
        
        # Build the complete prompt
        prompt = f"""You are an intelligent research assistant helping users prepare for meetings by providing insights from recent academic papers. You have access to relevant research papers and should provide accurate, well-informed responses based on the provided context.

{context_section}

{history_section}

Current question: {user_query}

Please provide a comprehensive and helpful response based on the research papers provided above. If the context doesn't contain enough information to fully answer the question, say so and suggest what additional information might be helpful."""
        
        return prompt
    
    def generate_response(
        self, 
        user_query: str, 
        conversation_history: List[Dict[str, str]] = None,
        use_cache: bool = True
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate a response using RAG.
        
        Args:
            user_query: User's question
            conversation_history: Previous conversation messages
            use_cache: Whether to use context caching
            
        Returns:
            Tuple of (response_text, retrieved_context)
        """
        # Retrieve relevant context
        if use_cache:
            retrieved_context = self.retrieve_context(user_query)
        else:
            retrieved_context = self.vector_db.search_similar(user_query, top_k=self.top_k)
        
        # Build RAG prompt
        prompt = self.build_rag_prompt(user_query, retrieved_context, conversation_history)
        
        # Generate response using LLM
        logger.info("Generating response with RAG...")
        response = self.llm_client.generate_response(prompt)
        
        return response, retrieved_context
    
    def generate_streaming_response(
        self, 
        user_query: str, 
        conversation_history: List[Dict[str, str]] = None,
        use_cache: bool = True
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        Generate a streaming response using RAG.
        
        Args:
            user_query: User's question
            conversation_history: Previous conversation messages
            use_cache: Whether to use context caching
            
        Returns:
            Tuple of (response_generator, retrieved_context)
        """
        # Retrieve relevant context
        if use_cache:
            retrieved_context = self.retrieve_context(user_query)
        else:
            retrieved_context = self.vector_db.search_similar(user_query, top_k=self.top_k)
        
        # Build RAG prompt
        prompt = self.build_rag_prompt(user_query, retrieved_context, conversation_history)
        
        # Generate streaming response using LLM
        logger.info("Generating streaming response with RAG...")
        response_generator = self.llm_client.generate_streaming_response(prompt)
        
        return response_generator, retrieved_context
    
    def _format_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """
        Format retrieved context documents for the prompt.
        
        Args:
            context_docs: Retrieved context documents
            
        Returns:
            Formatted context string
        """
        if not context_docs:
            return "No relevant context found."
        
        context_parts = ["Relevant Research Papers:"]
        
        for i, doc in enumerate(context_docs, 1):
            metadata = doc.get('metadata', {})
            title = metadata.get('title', 'Unknown Title')
            authors = metadata.get('authors', [])
            abstract = metadata.get('abstract', '')
            source = metadata.get('source', 'arxiv')
            
            # Format authors
            author_str = ", ".join(authors) if authors else "Unknown Authors"
            
            # Truncate abstract if too long
            if len(abstract) > 500:
                abstract = abstract[:500] + "..."
            
            context_parts.append(f"""
Paper {i}: {title}
Authors: {author_str}
Source: {source}
Abstract: {abstract}
""")
        
        return "\n".join(context_parts)
    
    def _format_conversation_history(self, history: List[Dict[str, str]] = None) -> str:
        """
        Format conversation history for the prompt with intelligent truncation.
        
        Args:
            history: Conversation history messages
            
        Returns:
            Formatted history string
        """
        if not history:
            return ""
        
        # Get recent messages (within context window)
        recent_messages = history[-self.context_window:] if len(history) > self.context_window else history
        
        if not recent_messages:
            return ""
        
        history_parts = ["Previous conversation:"]
        
        for msg in recent_messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            # Truncate very long responses to prevent context overflow
            if len(content) > 1000:  # Limit to 1000 characters per message
                content = content[:1000] + "... [truncated]"
            
            if role == 'user':
                history_parts.append(f"Human: {content}")
            elif role == 'assistant':
                history_parts.append(f"Assistant: {content}")
        
        return "\n".join(history_parts)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear the context cache."""
        self.cache.clear()


def create_rag_engine(
    vector_db: VectorDBPopulator,
    llm_client: LLMClient,
    config: Dict[str, Any]
) -> RAGEngine:
    """
    Create a RAG engine from configuration.
    
    Args:
        vector_db: Vector database populator
        llm_client: LLM client
        config: Configuration dictionary
        
    Returns:
        Configured RAGEngine instance
    """
    rag_config = config.get("rag", {})
    
    return RAGEngine(
        vector_db=vector_db,
        llm_client=llm_client,
        top_k=rag_config.get("top_k", 5),
        context_window=rag_config.get("context_window", 2),
        cache_ttl=rag_config.get("cache_ttl", 300),
        max_cache_size=rag_config.get("max_cache_size", 50)
    )


def main():
    """Test the RAG engine."""
    # This would require actual vector DB and LLM setup
    print("RAG Engine test would require vector DB and LLM setup")
    print("Use the main CLI scripts to test the full pipeline")


if __name__ == "__main__":
    main()
