#!/usr/bin/env python3
"""Command-line interface for the vector template."""

import argparse
import sys
import logging
import uvicorn
from pathlib import Path

# Add src to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vector_template.api.server import create_app
from vector_template.examples.recipe_example import RecipeVectorExample, run_example, run_csv_example
from vector_template.database.chroma_client import ChromaVectorDB
from vector_template.agents.smol_agent import SmolVectorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def serve_api(args):
    """Start the FastAPI server."""
    logger.info(f"Starting API server on {args.host}:{args.port}")
    
    app = create_app(
        persist_directory=args.db_path,
        collection_name=args.collection,
        host=args.chroma_host,
        port=args.chroma_port,
    )
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level.lower()
    )


def run_example_cmd(args):
    """Run the recipe example."""
    logger.info("Running recipe example")
    if args.csv_file:
        run_csv_example(args.csv_file)
    else:
        run_example()


def interactive_mode(args):
    """Start interactive mode with the vector database."""
    logger.info("Starting interactive mode")
    
    # Initialize database and agent
    db = ChromaVectorDB(
        persist_directory=args.db_path,
        collection_name=args.collection,
        host=args.chroma_host,
        port=args.chroma_port,
    )
    agent = SmolVectorAgent(vector_db=db)
    
    print("\\n" + "="*60)
    print("VECTOR TEMPLATE INTERACTIVE MODE")
    print("="*60)
    print("Available commands:")
    print("  add <text>           - Add a document")
    print("  search <query>       - Search documents")
    print("  info                 - Show collection info")
    print("  collections          - List collections")
    print("  switch <name>        - Switch collection")
    print("  reset                - Reset current collection")
    print("  agent <task>         - Run agent task")
    print("  quit                 - Exit")
    print("="*60)
    
    while True:
        try:
            command = input("\\nvector-template> ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            parts = command.split(' ', 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd == 'add':
                if not arg:
                    print("Usage: add <text>")
                    continue
                db.add_documents([arg])
                print("Document added successfully")
            
            elif cmd == 'search':
                if not arg:
                    print("Usage: search <query>")
                    continue
                results = db.query(arg, n_results=5)
                if results['documents'] and results['documents'][0]:
                    print(f"\\nFound {len(results['documents'][0])} results:")
                    for i, doc in enumerate(results['documents'][0]):
                        distance = results['distances'][0][i] if 'distances' in results else 'N/A'
                        print(f"\\n{i+1}. (Score: {1-float(distance):.3f})")
                        print(f"   {doc[:200]}{'...' if len(doc) > 200 else ''}")
                else:
                    print("No results found")
            
            elif cmd == 'info':
                info = db.get_collection_info()
                print(f"\\nCollection: {info['name']}")
                print(f"Documents: {info['count']}")
                print(f"Embedding: {info['embedding_function']}")
            
            elif cmd == 'collections':
                collections = db.list_collections()
                print(f"\\nAvailable collections: {', '.join(collections)}")
            
            elif cmd == 'switch':
                if not arg:
                    print("Usage: switch <collection_name>")
                    continue
                try:
                    db.switch_collection(arg)
                    print(f"Switched to collection: {arg}")
                except Exception as e:
                    print(f"Error switching collection: {e}")
            
            elif cmd == 'reset':
                confirm = input("Are you sure you want to reset the collection? (y/N): ")
                if confirm.lower() == 'y':
                    db.reset_collection()
                    print("Collection reset successfully")
                else:
                    print("Reset cancelled")
            
            elif cmd == 'agent':
                if not arg:
                    print("Usage: agent <task>")
                    continue
                try:
                    result = agent.run(arg)
                    print(f"\\nAgent result:\\n{result}")
                except Exception as e:
                    print(f"Error running agent task: {e}")
            
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'quit' to exit or see available commands above")
        
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Vector Template CLI - A tool for vector database operations with smolagents"
    )
    
    # Global arguments
    parser.add_argument(
        '--db-path',
        default='./chroma_db',
        help='Path to the vector database directory'
    )
    parser.add_argument(
        '--collection',
        default='default_collection',
        help='Name of the collection to use'
    )
    parser.add_argument(
        '--chroma-host',
        help='Chroma server host (for client-server mode)'
    )
    parser.add_argument(
        '--chroma-port',
        type=int,
        help='Chroma server port (for client-server mode)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Log level'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start the API server')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    serve_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    serve_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    serve_parser.set_defaults(func=serve_api)
    
    # Example command
    example_parser = subparsers.add_parser('example', help='Run the recipe example')
    example_parser.add_argument('--csv-file', help='Path to CSV file with recipes')
    example_parser.set_defaults(func=run_example_cmd)
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive mode')
    interactive_parser.set_defaults(func=interactive_mode)
    
    args = parser.parse_args()
    
    # Set up logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()