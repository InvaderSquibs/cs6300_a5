#!/usr/bin/env python3
"""
ArXiv Paper Population Script

This script fetches papers from arXiv for a given topic and populates a vector database
for use with the RAG chat system.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.arxiv_fetcher import fetch_papers_for_topic
from src.vector_db_populator import VectorDBPopulator
from src.config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sanitize_topic_name(topic: str) -> str:
    """
    Sanitize topic name for use as collection name.
    
    Args:
        topic: Original topic string
        
    Returns:
        Sanitized topic name
    """
    # Replace spaces and special characters with underscores
    sanitized = topic.lower().replace(" ", "_").replace("-", "_")
    # Remove non-alphanumeric characters except underscores
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    # Remove multiple consecutive underscores
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")
    return sanitized


def populate_arxiv_papers(topic: str, max_papers: int = 12, category: str = None) -> str:
    """
    Fetch and populate vector database with arXiv papers.
    
    Args:
        topic: Research topic to search for
        max_papers: Maximum number of papers to fetch
        category: Optional arXiv category filter
        
    Returns:
        Collection name used for the database
    """
    logger.info(f"🔍 Fetching top {max_papers} papers on '{topic}' from arXiv...")
    
    # Fetch papers from arXiv
    papers = fetch_papers_for_topic(
        topic=topic,
        max_papers=max_papers,
        category=category
    )
    
    if not papers:
        logger.error("❌ No papers found for the given topic")
        return None
    
    logger.info(f"📄 Found {len(papers)} papers")
    
    # Create sanitized collection name
    collection_name = f"arxiv_{sanitize_topic_name(topic)}"
    logger.info(f"📊 Creating vector database: '{collection_name}'")
    
    # Initialize vector database
    config = get_config()
    populator = VectorDBPopulator(backend_type='chromadb')
    populator.initialize_encoder()
    populator.initialize_database({
        'collection_name': collection_name
    })
    
    # Prepare texts and metadata for population
    texts = []
    metadata = []
    
    for paper in papers:
        # Use combined title + abstract for embedding
        texts.append(paper['text'])
        
        # Store metadata, filtering out None values for ChromaDB compatibility
        metadata_item = {
            'title': paper['title'],
            'abstract': paper['abstract'],
            'authors': paper['authors'],
            'categories': paper['categories'],
            'source': paper['source'],
            'arxiv_id': paper['id']
        }
        
        # Add optional fields only if they're not None
        if paper.get('primary_category'):
            metadata_item['primary_category'] = paper['primary_category']
        if paper.get('published'):
            metadata_item['published'] = paper['published']
        if paper.get('updated'):
            metadata_item['updated'] = paper['updated']
        if paper.get('pdf_url'):
            metadata_item['pdf_url'] = paper['pdf_url']
        if paper.get('doi'):
            metadata_item['doi'] = paper['doi']
        if paper.get('comment'):
            metadata_item['comment'] = paper['comment']
        if paper.get('journal_ref'):
            metadata_item['journal_ref'] = paper['journal_ref']
            
        metadata.append(metadata_item)
    
    # Populate the database
    logger.info("📚 Populating vector database...")
    populator.populate_from_texts(texts, metadata)
    
    logger.info(f"✅ Successfully populated database with {len(papers)} papers")
    return collection_name


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Fetch and populate vector database with arXiv papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python populate_arxiv.py "machine learning"
  python populate_arxiv.py "transformer architectures" --max-papers 20
  python populate_arxiv.py "neural networks" --category cs.LG
        """
    )
    
    parser.add_argument(
        "topic",
        help="Research topic to search for"
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
        # Populate the database
        collection_name = populate_arxiv_papers(
            topic=args.topic,
            max_papers=args.max_papers,
            category=args.category
        )
        
        if collection_name:
            print(f"\n🎉 Success! Vector database created: '{collection_name}'")
            print(f"💬 Ready to chat! Run: python rag_chat.py \"{args.topic}\"")
        else:
            print("❌ Failed to populate database")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
