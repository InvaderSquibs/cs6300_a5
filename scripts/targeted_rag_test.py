#!/usr/bin/env python3
"""
Targeted RAG Test - 12 Papers with Specific Questions

A focused test that fetches 12 papers on a specific topic and asks
very targeted, specific questions to test the RAG system's precision.

Usage: python3 targeted_rag_test.py --topic "neural networks" --max-papers 12
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.vector_db_populator import VectorDBPopulator
from src.llm_client import LLMClient, create_llm_client
from src.rag_engine import RAGEngine, create_rag_engine
from src.chat_manager import ChatManager, create_chat_manager
from src.arxiv_fetcher import fetch_papers_for_topic
from src.config import get_config


class TargetedRAGTest:
    """Targeted RAG test with specific, focused questions."""
    
    def __init__(self, topic: str, max_papers: int = 12):
        self.topic = topic
        self.max_papers = max_papers
        self.config = get_config()
        self.metrics = {
            "start_time": datetime.now().isoformat(),
            "topic": topic,
            "max_papers": max_papers,
            "pipeline_steps": {},
            "conversation": [],
            "performance": {},
            "cache_stats": {},
            "errors": []
        }
        
        # Very specific, targeted questions
        self.targeted_queries = [
            f"What specific algorithms or methods are mentioned in the {topic} papers?",
            f"What are the main experimental results and performance metrics reported in the {topic} research?",
            f"What datasets were used in the {topic} studies and what were the key findings?",
            f"What are the limitations and challenges identified in the {topic} papers?",
            f"What future work or research directions are suggested in the {topic} studies?",
            f"What mathematical formulations or equations are presented in the {topic} papers?",
            f"What are the key contributions and novel approaches in the {topic} research?",
            f"What evaluation metrics and benchmarks are used in the {topic} studies?"
        ]
    
    def run_targeted_test(self):
        """Run the targeted RAG test."""
        print("🎯 Targeted RAG Test - 12 Papers with Specific Questions")
        print("=" * 70)
        print(f"Topic: {self.topic}")
        print(f"Max Papers: {self.max_papers}")
        print("🎯 Goal: Test precision with targeted, specific questions")
        print("=" * 70)
        
        try:
            # Step 1: Fetch papers from arXiv
            self._step1_fetch_papers()
            
            # Step 2: Populate vector database
            self._step2_populate_database()
            
            # Step 3: Initialize RAG system
            self._step3_initialize_rag()
            
            # Step 4: Run targeted conversation test
            self._step4_run_targeted_conversation()
            
            # Step 5: Generate report
            self._step5_generate_report()
            
            print("\n🎉 Targeted RAG Test Completed!")
            self._print_summary()
            
        except Exception as e:
            error_msg = f"Test failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.metrics["errors"].append(error_msg)
            raise
    
    def _step1_fetch_papers(self):
        """Step 1: Fetch papers from arXiv."""
        print(f"\n📚 Step 1: Fetching {self.max_papers} papers on '{self.topic}' from arXiv...")
        
        start_time = time.time()
        
        try:
            papers = fetch_papers_for_topic(
                topic=self.topic,
                max_papers=self.max_papers
            )
            
            fetch_time = time.time() - start_time
            
            self.metrics["pipeline_steps"]["fetch_papers"] = {
                "status": "success",
                "papers_found": len(papers),
                "time_seconds": fetch_time,
                "papers": [
                    {
                        "title": paper["title"],
                        "authors": paper["authors"],
                        "published": paper.get("published", "Unknown"),
                        "pdf_url": paper.get("pdf_url", "N/A")
                    }
                    for paper in papers
                ]
            }
            
            print(f"✅ Successfully fetched {len(papers)} papers in {fetch_time:.2f} seconds")
            
            # Store papers for next step
            self.papers = papers
            
        except Exception as e:
            error_msg = f"Failed to fetch papers: {str(e)}"
            print(f"❌ {error_msg}")
            self.metrics["errors"].append(error_msg)
            raise
    
    def _step2_populate_database(self):
        """Step 2: Populate vector database."""
        print(f"\n🗄️ Step 2: Populating vector database with {len(self.papers)} papers...")
        
        start_time = time.time()
        
        try:
            # Initialize vector database
            collection_name = f"arxiv_{self.topic.lower().replace(' ', '_')}"
            self.vector_db = VectorDBPopulator(backend_type='chromadb')
            self.vector_db.initialize_encoder()
            self.vector_db.initialize_database({'collection_name': collection_name})
            
            # Prepare texts and metadata
            texts = []
            metadata = []
            
            for paper in self.papers:
                texts.append(paper['text'])
                
                # Store metadata, filtering out None values
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
            self.vector_db.populate_from_texts(texts, metadata)
            
            populate_time = time.time() - start_time
            
            self.metrics["pipeline_steps"]["populate_database"] = {
                "status": "success",
                "collection_name": collection_name,
                "documents_added": len(texts),
                "time_seconds": populate_time
            }
            
            print(f"✅ Successfully populated database '{collection_name}' with {len(texts)} documents in {populate_time:.2f} seconds")
            
        except Exception as e:
            error_msg = f"Failed to populate database: {str(e)}"
            print(f"❌ {error_msg}")
            self.metrics["errors"].append(error_msg)
            raise
    
    def _step3_initialize_rag(self):
        """Step 3: Initialize RAG system."""
        print(f"\n🤖 Step 3: Initializing RAG system...")
        
        start_time = time.time()
        
        try:
            # Initialize LLM client
            self.llm_client = create_llm_client(self.config)
            
            # Test LLM connection
            if not self.llm_client.check_connection():
                raise RuntimeError("Failed to connect to LM Studio")
            
            # Initialize RAG engine
            self.rag_engine = create_rag_engine(self.vector_db, self.llm_client, self.config)
            
            # Initialize chat manager
            self.chat_manager = create_chat_manager(self.config)
            self.session = self.chat_manager.start_new_session(self.topic)
            
            init_time = time.time() - start_time
            
            self.metrics["pipeline_steps"]["initialize_rag"] = {
                "status": "success",
                "llm_model": self.config["llm"]["model"],
                "llm_base_url": self.config["llm"]["base_url"],
                "rag_top_k": self.config["rag"]["top_k"],
                "time_seconds": init_time
            }
            
            print(f"✅ RAG system initialized successfully in {init_time:.2f} seconds")
            print(f"   LLM: {self.config['llm']['model']}")
            print(f"   Retrieval: Top-{self.config['rag']['top_k']} documents")
            
        except Exception as e:
            error_msg = f"Failed to initialize RAG system: {str(e)}"
            print(f"❌ {error_msg}")
            self.metrics["errors"].append(error_msg)
            raise
    
    def _step4_run_targeted_conversation(self):
        """Step 4: Run targeted conversation test."""
        print(f"\n🎯 Step 4: Running Targeted Question Test")
        print("🎯 Testing precision with specific, focused questions...")
        print("=" * 70)
        
        start_time = time.time()
        
        try:
            for i, query in enumerate(self.targeted_queries, 1):
                print(f"\n🎯 Question {i}: {query}")
                print("-" * 70)
                
                query_start = time.time()
                
                try:
                    # Get conversation history
                    conversation_history = self.session.get_conversation_history()
                    
                    # Generate response using RAG
                    print("🔍 Retrieving relevant context...")
                    response, retrieved_context = self.rag_engine.generate_response(
                        query, 
                        conversation_history
                    )
                    
                    # Calculate timing
                    response_time = time.time() - query_start
                    
                    # Add to session
                    self.chat_manager.add_message("user", query, retrieved_context)
                    self.chat_manager.add_message("assistant", response)
                    
                    # Store metrics
                    self.metrics["conversation"].append({
                        "query_number": i,
                        "user_query": query,
                        "assistant_response": response,
                        "response_time_seconds": response_time,
                        "context_papers_used": len(retrieved_context),
                        "context_titles": [ctx.get('metadata', {}).get('title', 'Unknown') for ctx in retrieved_context],
                        "response_length": len(response),
                        "specificity_score": self._calculate_specificity_score(query, response)
                    })
                    
                    # Display response with analysis
                    print(f"🤖 Assistant Response:")
                    print(f"   {response[:400]}{'...' if len(response) > 400 else ''}")
                    print(f"\n📊 Analysis:")
                    print(f"   📄 Used {len(retrieved_context)} relevant papers")
                    print(f"   ⏱️  Response time: {response_time:.2f} seconds")
                    print(f"   📝 Response length: {len(response)} characters")
                    print(f"   🎯 Specificity score: {self._calculate_specificity_score(query, response):.2f}")
                    
                except Exception as e:
                    error_msg = f"Question {i} failed: {str(e)}"
                    print(f"❌ {error_msg}")
                    self.metrics["errors"].append(error_msg)
            
            conversation_time = time.time() - start_time
            
            # Final metrics
            self.metrics["pipeline_steps"]["run_conversation"] = {
                "status": "success",
                "total_queries": len(self.targeted_queries),
                "successful_queries": len([q for q in self.metrics["conversation"]]),
                "time_seconds": conversation_time
            }
            
            print(f"\n✅ Targeted question test completed in {conversation_time:.2f} seconds")
            
        except Exception as e:
            error_msg = f"Failed to run conversation: {str(e)}"
            print(f"❌ {error_msg}")
            self.metrics["errors"].append(error_msg)
            raise
    
    def _calculate_specificity_score(self, query: str, response: str) -> float:
        """Calculate how specific and targeted the response is."""
        # Look for specific indicators in the response
        specificity_indicators = [
            "algorithm", "method", "experiment", "result", "dataset", "metric",
            "performance", "accuracy", "precision", "recall", "F1", "loss",
            "neural", "network", "model", "training", "validation", "test",
            "equation", "formula", "mathematical", "statistical", "benchmark"
        ]
        
        response_lower = response.lower()
        found_indicators = sum(1 for indicator in specificity_indicators if indicator in response_lower)
        
        # Normalize score (0-1)
        max_indicators = len(specificity_indicators)
        return min(found_indicators / max_indicators, 1.0)
    
    def _step5_generate_report(self):
        """Step 5: Generate comprehensive report."""
        print(f"\n📊 Step 5: Generating Targeted Test Report...")
        
        start_time = time.time()
        
        try:
            # Calculate performance metrics
            successful_conversations = [q for q in self.metrics["conversation"]]
            
            self.metrics["performance"] = {
                "total_queries": len(self.targeted_queries),
                "successful_queries": len(successful_conversations),
                "average_response_time": sum(q["response_time_seconds"] for q in successful_conversations) / len(successful_conversations) if successful_conversations else 0,
                "total_papers_retrieved": sum(q["context_papers_used"] for q in successful_conversations),
                "average_response_length": sum(q["response_length"] for q in successful_conversations) / len(successful_conversations) if successful_conversations else 0,
                "average_specificity_score": sum(q["specificity_score"] for q in successful_conversations) / len(successful_conversations) if successful_conversations else 0,
                "pipeline_total_time": time.time() - time.mktime(datetime.fromisoformat(self.metrics["start_time"]).timetuple())
            }
            
            # Cache stats
            self.metrics["cache_stats"] = self.rag_engine.get_cache_stats()
            
            # End time
            self.metrics["end_time"] = datetime.now().isoformat()
            
            # Save detailed report
            report_file = f"targeted_rag_test_report_{self.topic.lower().replace(' ', '_')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)
            
            report_time = time.time() - start_time
            
            self.metrics["pipeline_steps"]["generate_report"] = {
                "status": "success",
                "report_file": report_file,
                "time_seconds": report_time
            }
            
            print(f"✅ Report generated: {report_file}")
            
        except Exception as e:
            error_msg = f"Failed to generate report: {str(e)}"
            print(f"❌ {error_msg}")
            self.metrics["errors"].append(error_msg)
            raise
    
    def _print_summary(self):
        """Print a summary of the test results."""
        print("\n" + "=" * 80)
        print("TARGETED RAG TEST SUMMARY")
        print("=" * 80)
        print(f"Topic: {self.metrics['topic']}")
        print(f"Papers Fetched: {self.metrics['pipeline_steps']['fetch_papers']['papers_found']}")
        print(f"Database: {self.metrics['pipeline_steps']['populate_database']['collection_name']}")
        print(f"Documents Added: {self.metrics['pipeline_steps']['populate_database']['documents_added']}")
        print(f"LLM Model: {self.metrics['pipeline_steps']['initialize_rag']['llm_model']}")
        print(f"Questions Tested: {self.metrics['performance']['total_queries']}")
        print(f"Successful Questions: {self.metrics['performance']['successful_queries']}")
        print(f"Average Response Time: {self.metrics['performance']['average_response_time']:.2f}s")
        print(f"Average Response Length: {self.metrics['performance']['average_response_length']:.0f} characters")
        print(f"Average Specificity Score: {self.metrics['performance']['average_specificity_score']:.2f}")
        print(f"Total Papers Retrieved: {self.metrics['performance']['total_papers_retrieved']}")
        print(f"Cache Usage: {self.metrics['cache_stats']['size']}/{self.metrics['cache_stats']['max_size']}")
        print(f"Total Pipeline Time: {self.metrics['performance']['pipeline_total_time']:.2f}s")
        
        if self.metrics["errors"]:
            print(f"\nErrors: {len(self.metrics['errors'])}")
            for error in self.metrics["errors"]:
                print(f"  ❌ {error}")
        
        print("\n" + "=" * 80)
        print("🎉 Targeted RAG Test completed!")
        print("📁 Check the generated report for detailed metrics and conversation logs.")
        print("🎯 The RAG system was tested with specific, targeted questions!")


def main():
    """Main function to run the targeted RAG test."""
    parser = argparse.ArgumentParser(description="Targeted RAG Test - 12 Papers with Specific Questions")
    parser.add_argument("--topic", type=str, default="neural networks", help="Topic to search for papers")
    parser.add_argument("--max-papers", type=int, default=12, help="Maximum number of papers to fetch")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    print("🎯 Targeted RAG Test - 12 Papers with Specific Questions")
    print("=" * 60)
    print(f"Topic: {args.topic}")
    print(f"Max Papers: {args.max_papers}")
    print("🎯 Goal: Test precision with targeted, specific questions")
    print("=" * 60)
    
    try:
        # Run the targeted test
        test = TargetedRAGTest(args.topic, args.max_papers)
        test.run_targeted_test()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
