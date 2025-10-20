#!/usr/bin/env python3
"""
Command line interface for recipe similarity evaluation.

Usage:
    python cli.py --input recipes.json --threshold 0.7 --output results.json
    python cli.py --sample  # Create sample data file
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.comparator import RecipeSimilarityComparator
from src.utils import load_recipes_from_json, save_results_to_json, create_sample_json_file
from config.config import MODEL_NAME, SIMILARITY_THRESHOLD, LOG_LEVEL, LOG_FORMAT


def setup_logging(level: str = LOG_LEVEL):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=LOG_FORMAT
    )


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Recipe Similarity Evaluation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --input recipes.json --output results.json
  python cli.py --input recipes.json --threshold 0.8 --model all-mpnet-base-v2
  python cli.py --sample --output sample_recipes.json
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input JSON file containing recipe data"
    )
    
    parser.add_argument(
        "--output", "-o", 
        type=str,
        default="similarity_results.json",
        help="Output JSON file for results (default: similarity_results.json)"
    )
    
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=SIMILARITY_THRESHOLD,
        help=f"Similarity threshold (default: {SIMILARITY_THRESHOLD})"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=MODEL_NAME,
        help=f"Model name to use (default: {MODEL_NAME})"
    )
    
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="./models",
        help="Directory to cache models (default: ./models)"
    )
    
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Create a sample JSON file with recipe data"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else LOG_LEVEL
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    try:
        if args.sample:
            # Create sample file
            output_path = args.output if args.output != "similarity_results.json" else "sample_recipes.json"
            create_sample_json_file(output_path)
            print(f"Sample recipe file created: {output_path}")
            return
        
        if not args.input:
            parser.error("--input is required unless using --sample")
        
        # Validate threshold
        if not 0 <= args.threshold <= 1:
            parser.error("Threshold must be between 0 and 1")
        
        # Load recipe data
        logger.info(f"Loading recipes from: {args.input}")
        response = load_recipes_from_json(args.input)
        
        logger.info(
            f"Loaded target recipe: {response.target_recipe.title}, "
            f"Candidates: {len(response.candidate_recipes)}"
        )
        
        # Initialize comparator
        logger.info(f"Initializing comparator with model: {args.model}")
        comparator = RecipeSimilarityComparator(
            model_name=args.model,
            cache_dir=args.cache_dir,
            similarity_threshold=args.threshold
        )
        
        # Download and load model
        comparator.initialize()
        
        # Perform comparison
        logger.info("Performing recipe similarity comparison...")
        results = comparator.compare_recipes(response)
        
        # Save results
        save_results_to_json(
            results,
            response.target_recipe,
            response.candidate_recipes,
            args.output
        )
        
        # Display summary
        summary = comparator.get_similarity_summary(results)
        
        print(f"\n{'='*50}")
        print("RECIPE SIMILARITY EVALUATION COMPLETE")
        print(f"{'='*50}")
        print(f"Target Recipe: {response.target_recipe.title}")
        print(f"Total Comparisons: {summary['total_comparisons']}")
        print(f"Similar Recipes: {summary['similar_recipes']}")
        print(f"Similarity Rate: {summary['similarity_rate']:.1%}")
        print(f"Average Score: {summary['average_similarity_score']:.3f}")
        print(f"Threshold Used: {args.threshold}")
        print(f"Results saved to: {args.output}")
        print(f"{'='*50}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()