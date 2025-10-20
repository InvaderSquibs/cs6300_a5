#!/usr/bin/env python3
"""
ArXiv RAG Pipeline Demo

This script orchestrates the complete workflow:
1. Fetch papers from arXiv for a topic
2. Populate vector database
3. Initialize RAG chat system
4. Start interactive chat session
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.arxiv_fetcher import fetch_papers_for_topic
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


def fetch_and_populate_papers(topic: str, max_papers: int = 12, category: str = None) -> str:
    """
    Fetch papers from arXiv and populate vector database.
    
    Args:
        topic: Research topic
        max_papers: Maximum number of papers
        category: Optional arXiv category
        
    Returns:
        Collection name
    """
    print(f"🔍 Step 1: Fetching papers from arXiv...")
    print(f"   Topic: {topic}")
    print(f"   Max papers: {max_papers}")
    if category:
        print(f"   Category: {category}")
    
    # Fetch papers
    papers = fetch_papers_for_topic(
        topic=topic,
        max_papers=max_papers,
        category=category
    )
    
    if not papers:
        raise RuntimeError("❌ No papers found for the given topic")
    
    print(f"   ✓ Retrieved {len(papers)} papers")
    
    # Create collection name
    collection_name = f"arxiv_{sanitize_topic_name(topic)}"
    
    print(f"\n📊 Step 2: Building vector database...")
    print(f"   Collection: {collection_name}")
    
    # Initialize vector database
    populator = VectorDBPopulator(backend_type='chromadb')
    populator.initialize_encoder()
    populator.initialize_database({
        'collection_name': collection_name
    })
    
    # Prepare data
    texts = [paper['text'] for paper in papers]
    metadata = []
    
    for paper in papers:
        metadata.append({
            'title': paper['title'],
            'abstract': paper['abstract'],
            'authors': paper['authors'],
            'categories': paper['categories'],
            'primary_category': paper['primary_category'],
            'published': paper['published'],
            'updated': paper['updated'],
            'pdf_url': paper['pdf_url'],
            'doi': paper['doi'],
            'comment': paper['comment'],
            'journal_ref': paper['journal_ref'],
            'source': paper['source'],
            'arxiv_id': paper['id']
        })
    
    # Populate database
    populator.populate_from_texts(texts, metadata)
    print(f"   ✓ Created collection: {collection_name}")
    print(f"   ✓ Embedded and stored {len(papers)} papers")
    
    return collection_name


def initialize_rag_system(topic: str) -> tuple[RAGEngine, ChatManager]:
    """
    Initialize the RAG system.
    
    Args:
        topic: Research topic
        
    Returns:
        Tuple of (RAG engine, chat manager)
    """
    print(f"\n🤖 Step 3: Initializing RAG system...")
    
    # Load configuration
    config = get_config()
    
    # Initialize LLM client
    print("   Initializing LLM client...")
    llm_client = create_llm_client(config)
    
    if not llm_client.check_connection():
        raise RuntimeError("❌ Failed to connect to Ollama. Make sure Ollama is running and the model is available.")
    
    print("   ✓ Connected to Qwen LLM")
    
    # Initialize vector database
    collection_name = f"arxiv_{sanitize_topic_name(topic)}"
    vector_db = VectorDBPopulator(backend_type='chromadb')
    vector_db.initialize_encoder()
    vector_db.initialize_database({'collection_name': collection_name})
    
    # Create RAG engine
    rag_engine = create_rag_engine(vector_db, llm_client, config)
    
    # Create chat manager
    chat_manager = create_chat_manager(config)
    
    print("   ✓ RAG system initialized")
    
    return rag_engine, chat_manager


def chat_loop(rag_engine: RAGEngine, chat_manager: ChatManager, topic: str):
    """
    Main chat loop.
    
    Args:
        rag_engine: RAG engine
        chat_manager: Chat manager
        topic: Research topic
    """
    # Start new session
    session = chat_manager.start_new_session(topic)
    
    print(f"\n💬 Chat started for topic: '{topic}'")
    print("Type 'quit' to exit, 'save' to save session, 'help' for commands")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
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
            
            # Generate response
            print("🔍 Retrieving relevant context...")
            
            conversation_history = session.get_conversation_history()
            response, retrieved_context = rag_engine.generate_response(
                user_input, 
                conversation_history
            )
            
            # Add to session
            chat_manager.add_message("user", user_input, retrieved_context)
            chat_manager.add_message("assistant", response)
            
            # Display response
            print(f"\nAssistant: {response}")
            
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
    cache_stats = rag_engine.get_cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"  TTL: {cache_stats['ttl_seconds']} seconds")
    
    session = chat_manager.get_current_session()
    if session:
        summary = chat_manager.get_session_summary()
        print(f"\n💬 Session Statistics:")
        print(f"  Session ID: {summary['session_id']}")
        print(f"  Topic: {summary['topic']}")
        print(f"  Messages: {summary['total_messages']}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Complete ArXiv RAG pipeline demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_pipeline.py
  python demo_pipeline.py --topic "machine learning" --max-papers 20
  python demo_pipeline.py --topic "transformer architectures" --category cs.LG
        """
    )
    
    parser.add_argument(
        "--topic",
        help="Research topic (will prompt if not provided)"
    )
    
    parser.add_argument(
        "--max-papers",
        type=int,
        default=12,
        help="Maximum number of papers to fetch (default: 12)"
    )
    
    parser.add_argument(
        "--category",
        help="ArXiv category filter (e.g., cs.AI, cs.LG, stat.ML)"
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
        print("🎯 ArXiv RAG Meeting Prep Assistant")
        print("=" * 40)
        
        # Get topic if not provided
        if not args.topic:
            args.topic = input("\nEnter research topic: ").strip()
            if not args.topic:
                print("❌ Topic is required")
                sys.exit(1)
        
        # Step 1: Fetch and populate papers
        collection_name = fetch_and_populate_papers(
            topic=args.topic,
            max_papers=args.max_papers,
            category=args.category
        )
        
        # Step 2: Initialize RAG system
        rag_engine, chat_manager = initialize_rag_system(args.topic)
        
        print("\n" + "=" * 40)
        print("✅ Setup complete! You can now chat with the assistant.")
        print(f"💡 The assistant has context from {args.max_papers} recent papers on \"{args.topic}\"")
        print("=" * 40)
        
        # Step 3: Start chat
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
