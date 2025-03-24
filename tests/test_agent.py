#!/usr/bin/env python3
"""
Test script for the ArXiv Research Assistant agent.

This script tests the functionality of the ArXiv Research Assistant agent.
"""

import os
import sys
import traceback

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main test function."""
    print("Testing ArXiv Research Assistant...")
    
    try:
        # Import the agent module
        from arxiv_agents import get_arxiv_assistant, search_papers
        
        # Test direct tool usage
        print("\n1. Testing direct tool usage...")
        result = search_papers("machine learning", limit=1, auto_download=True)
        print(f"Search result: Success = {result['success']}")
        print(f"Found {result['total_papers']} papers")
        
        if result["papers"]:
            paper = result["papers"][0]
            print(f"\nTitle: {paper['title']}")
            print(f"Authors: {paper['authors']}")
            print(f"Summary: {paper.get('summary', 'No summary available')[:150]}...")
        
        # Test the agent
        print("\n2. Testing agent with query...")
        assistant = get_arxiv_assistant("ArXiv Research Expert")
        print(f"Created agent: {assistant.name}")
        
        response = assistant.run("Find me 1 paper about quantum computing")
        print("\nResponse from agent:")
        print(response)
        
        print("\nAll tests completed successfully!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure the OpenAI Agents SDK is installed: pip install openai-agents")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()