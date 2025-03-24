#!/usr/bin/env python3
"""
Test script for the arXiv Agent Wrapper functionality.
"""

import sys
import os

# Add parent directory to path so we can import the agent_wrapper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the agent_wrapper
from agent_wrapper import ArxivTool, ArxivBatchParams, ArxivListParams

def test_wrapper():
    """Test the basic functionality of the agent wrapper."""
    # Create the arXiv tool
    tool = ArxivTool()
    
    # List downloaded papers
    list_result = tool.list_papers()
    print(f"List result: {list_result.message}")
    print(f"Total papers: {len(list_result.papers) if list_result.papers else 0}")
    
    # If we have papers, display the first one
    if list_result.papers:
        paper = list_result.papers[0]
        print(f"\nExample paper:")
        print(f"  Title: {paper.title}")
        print(f"  Authors: {paper.authors}")
        print(f"  Paper ID: {paper.paper_id}")
        print(f"  Primary Category: {paper.primary_category}")
        if paper.summary:
            summary = paper.summary[:100] + "..." if len(paper.summary) > 100 else paper.summary
            print(f"  Summary: {summary}")
    
    # Batch download a specific paper
    print("\nBatch downloading a paper...")
    batch_result = tool.batch_download(ArxivBatchParams(
        paper_ids=["2110.03608"],  # A specific paper ID
        delay=3.0
    ))
    print(f"Batch download result: {batch_result.message}")
    print(f"Download stats: {batch_result.data}")
    
    # Now list papers again to verify download worked
    list_result = tool.list_papers()
    print(f"Updated list result: {list_result.message}")
    
    # Display downloaded paper details
    if list_result.papers:
        paper = list_result.papers[0]
        print(f"\nDownloaded paper:")
        print(f"  Title: {paper.title}")
        print(f"  Authors: {paper.authors}")
        print(f"  Paper ID: {paper.paper_id}")
        print(f"  Primary Category: {paper.primary_category}")
        if paper.summary:
            summary = paper.summary[:100] + "..." if len(paper.summary) > 100 else paper.summary
            print(f"  Summary: {summary}")

if __name__ == "__main__":
    test_wrapper()