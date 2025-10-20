#!/usr/bin/env python3
"""
RAG Chat Interface

This script provides an interactive chat interface with RAG capabilities,
allowing users to chat with an LLM that has context from arXiv papers.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.vector_db_populator import VectorDBPopulator
from src.llm_client import LLMClient, create_llm_client
from src.rag_engine import RAGEngine, create_rag_engine
from src.chat_manager import ChatManager, create_chat_manager
from src.config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sanitize_topic_name(topic: str) -> str:
    """Sanitize topic name for use as collection name."""
    sanitized = topic.lower().replace(" ", "_").replace("-", "_")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    return sanitized.strip("_")


def load_vector_database(topic: str) -> VectorDBPopulator:
    """
    Load the vector database for a given topic.
    
    Args:
        topic: Research topic
        
    Returns:
        Initialized vector database populator
    """
    collection_name = f"arxiv_{sanitize_topic_name(topic)}"
    
    logger.info(f"📚 Loading vector database: '{collection_name}'")
    
    # Initialize vector database
    populator = VectorDBPopulator(backend_type='chromadb')
    populator.initialize_encoder()
    populator.initialize_database({
        'collection_name': collection_name
    })
    
    return populator


def initialize_llm() -> LLMClient:
    """
    Initialize the LLM client.
    
    Returns:
        Initialized LLM client
    """
    logger.info("🤖 Initializing LLM client...")
    
    config = get_config()
    llm_client = create_llm_client(config)
    
    # Test connection
    if not llm_client.check_connection():
        raise RuntimeError("❌ Failed to connect to Ollama. Make sure Ollama is running and the model is available.")
    
    logger.info("✅ LLM client initialized successfully")
    return llm_client


def initialize_rag_system(topic: str) -> tuple[RAGEngine, ChatManager]:
    """
    Initialize the complete RAG system.
    
    Args:
        topic: Research topic
        
    Returns:
        Tuple of (RAG engine, chat manager)
    """
    # Load configuration
    config = get_config()
    
    # Initialize components
    vector_db = load_vector_database(topic)
    llm_client = initialize_llm()
    chat_manager = create_chat_manager(config)
    
    # Create RAG engine
    rag_engine = create_rag_engine(vector_db, llm_client, config)
    
    return rag_engine, chat_manager


def chat_loop(rag_engine: RAGEngine, chat_manager: ChatManager, topic: str):
    """
    Main chat loop.
    
    Args:
        rag_engine: RAG engine for context retrieval
        chat_manager: Chat manager for session handling
        topic: Research topic
    """
    # Start new chat session
    session = chat_manager.start_new_session(topic)
    
    print(f"\n💬 Chat started for topic: '{topic}'")
    print("Type 'quit' to exit, 'save' to save session, 'help' for commands")
    print("=" * 60)
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'save':
                if chat_manager.save_session():
                    print("💾 Session saved successfully!")
                else:
                    print("❌ Failed to save session")
                continue
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'stats':
                print_stats(rag_engine, chat_manager)
                continue
            
            # Generate response using RAG
            print("🔍 Retrieving relevant context...")
            
            # Get conversation history
            conversation_history = session.get_conversation_history()
            
            # Generate response
            response, retrieved_context = rag_engine.generate_response(
                user_input, 
                conversation_history
            )
            
            # Add messages to session
            chat_manager.add_message("user", user_input, retrieved_context)
            chat_manager.add_message("assistant", response)
            
            # Display response
            print(f"\nAssistant: {response}")
            
            # Show context info (optional)
            if retrieved_context:
                print(f"\n📚 Used {len(retrieved_context)} relevant papers")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            print(f"❌ Error: {e}")


def print_help():
    """Print help information."""
    print("""
Available commands:
  quit    - Exit the chat
  save    - Save current session
  stats   - Show cache and session statistics
  help    - Show this help message
""")


def print_stats(rag_engine: RAGEngine, chat_manager: ChatManager):
    """Print system statistics."""
    # Cache stats
    cache_stats = rag_engine.get_cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"  TTL: {cache_stats['ttl_seconds']} seconds")
    
    # Session stats
    session = chat_manager.get_current_session()
    if session:
        summary = chat_manager.get_session_summary()
        print(f"\n💬 Session Statistics:")
        print(f"  Session ID: {summary['session_id']}")
        print(f"  Topic: {summary['topic']}")
        print(f"  Messages: {summary['total_messages']}")
        print(f"  Created: {summary['created_at']}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Interactive RAG chat with arXiv papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rag_chat.py "machine learning"
  python rag_chat.py "transformer architectures" --session-id abc123
  python rag_chat.py "neural networks" --verbose
        """
    )
    
    parser.add_argument(
        "topic",
        help="Research topic to chat about"
    )
    
    parser.add_argument(
        "--session-id",
        help="Load existing session by ID"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize RAG system
        print("🚀 Initializing RAG system...")
        rag_engine, chat_manager = initialize_rag_system(args.topic)
        
        # Load existing session if specified
        if args.session_id:
            session = chat_manager.load_session(args.session_id)
            if session:
                print(f"📂 Loaded existing session: {args.session_id}")
            else:
                print(f"⚠️  Session not found: {args.session_id}")
                print("Starting new session...")
        
        # Start chat loop
        chat_loop(rag_engine, chat_manager, args.topic)
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
