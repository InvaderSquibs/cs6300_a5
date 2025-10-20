#!/usr/bin/env python3
"""
Generate Test Summary Report

Creates a comprehensive summary of all RAG system tests and demonstrations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def generate_test_summary():
    """Generate a comprehensive test summary report."""
    
    print("📊 Generating RAG System Test Summary")
    print("=" * 50)
    
    # Find all test reports
    test_reports = []
    
    # Look for various report files
    report_patterns = [
        "rag_conversation_report_*.json",
        "complete_rag_demo_report_*.json", 
        "smart_person_demo_report_*.json"
    ]
    
    for pattern in report_patterns:
        for report_file in Path(".").glob(pattern):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    report_data['report_file'] = str(report_file)
                    test_reports.append(report_data)
            except Exception as e:
                print(f"⚠️  Could not load {report_file}: {e}")
    
    if not test_reports:
        print("❌ No test reports found")
        return
    
    # Generate summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_tests": len(test_reports),
        "test_summary": [],
        "overall_metrics": {
            "total_queries": 0,
            "successful_queries": 0,
            "total_papers_fetched": 0,
            "total_papers_retrieved": 0,
            "average_response_time": 0,
            "total_errors": 0
        }
    }
    
    # Process each test report
    for report in test_reports:
        test_info = {
            "test_type": report.get('topic', 'Unknown'),
            "start_time": report.get('start_time', 'Unknown'),
            "end_time": report.get('end_time', 'Unknown'),
            "papers_fetched": 0,
            "queries_tested": 0,
            "successful_queries": 0,
            "average_response_time": 0,
            "errors": len(report.get('errors', [])),
            "report_file": report.get('report_file', 'Unknown')
        }
        
        # Extract metrics from different report formats
        if 'pipeline_steps' in report:
            # Complete demo format
            if 'fetch_papers' in report['pipeline_steps']:
                test_info['papers_fetched'] = report['pipeline_steps']['fetch_papers'].get('papers_found', 0)
            
            if 'run_conversation' in report['pipeline_steps']:
                test_info['queries_tested'] = report['pipeline_steps']['run_conversation'].get('total_queries', 0)
                test_info['successful_queries'] = report['pipeline_steps']['run_conversation'].get('successful_queries', 0)
        
        if 'performance' in report:
            test_info['average_response_time'] = report['performance'].get('average_response_time', 0)
        
        if 'conversation' in report:
            test_info['queries_tested'] = len(report['conversation'])
            test_info['successful_queries'] = len([q for q in report['conversation']])
        
        summary['test_summary'].append(test_info)
        
        # Update overall metrics
        summary['overall_metrics']['total_queries'] += test_info['queries_tested']
        summary['overall_metrics']['successful_queries'] += test_info['successful_queries']
        summary['overall_metrics']['total_papers_fetched'] += test_info['papers_fetched']
        summary['overall_metrics']['total_errors'] += test_info['errors']
        
        if test_info['average_response_time'] > 0:
            summary['overall_metrics']['average_response_time'] += test_info['average_response_time']
    
    # Calculate overall averages
    if summary['overall_metrics']['total_queries'] > 0:
        summary['overall_metrics']['success_rate'] = (
            summary['overall_metrics']['successful_queries'] / 
            summary['overall_metrics']['total_queries'] * 100
        )
    
    if len([t for t in summary['test_summary'] if t['average_response_time'] > 0]) > 0:
        avg_times = [t['average_response_time'] for t in summary['test_summary'] if t['average_response_time'] > 0]
        summary['overall_metrics']['average_response_time'] = sum(avg_times) / len(avg_times)
    
    # Save summary
    summary_file = "rag_system_test_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n📈 RAG System Test Summary")
    print("=" * 50)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Total Queries: {summary['overall_metrics']['total_queries']}")
    print(f"Successful Queries: {summary['overall_metrics']['successful_queries']}")
    print(f"Success Rate: {summary['overall_metrics'].get('success_rate', 0):.1f}%")
    print(f"Total Papers Fetched: {summary['overall_metrics']['total_papers_fetched']}")
    print(f"Average Response Time: {summary['overall_metrics']['average_response_time']:.2f}s")
    print(f"Total Errors: {summary['overall_metrics']['total_errors']}")
    
    print(f"\n📋 Individual Test Results:")
    print("-" * 50)
    for i, test in enumerate(summary['test_summary'], 1):
        print(f"{i}. {test['test_type']}")
        print(f"   Papers: {test['papers_fetched']}, Queries: {test['queries_tested']}")
        print(f"   Success: {test['successful_queries']}/{test['queries_tested']}")
        print(f"   Avg Time: {test['average_response_time']:.2f}s")
        print(f"   Errors: {test['errors']}")
        print()
    
    print(f"✅ Summary saved to: {summary_file}")
    
    # Check for chat histories
    chat_dir = Path("chat_history")
    if chat_dir.exists():
        chat_files = list(chat_dir.glob("*.json"))
        print(f"💬 Chat Histories: {len(chat_files)} sessions found")
        print(f"   Run 'python3 chat_viewer_gui.py' to view conversations")
    
    print(f"\n🎉 RAG System Testing Complete!")
    print(f"📁 Check individual report files for detailed metrics")
    print(f"🖥️  Use the GUI to view chat conversations")


if __name__ == "__main__":
    generate_test_summary()
