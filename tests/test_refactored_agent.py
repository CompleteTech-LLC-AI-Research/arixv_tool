#!/usr/bin/env python3
"""
Test script for the refactored ArXiv Research Assistant agent.
"""

import os
import sys

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the refactored agent
    from agents import get_arxiv_assistant, search_papers
    
    print("Testing ArXiv Research Assistant...")
    
    # Get the singleton instance
    assistant = get_arxiv_assistant("ArXiv Research Expert")
    
    if assistant:
        print(f"Agent created successfully: {assistant.name}")
        
        # First, test the direct tool usage (works without Agent SDK)
        print("\nTesting direct tool usage...")
        query = "reinforcement learning"
        print(f"Search query: '{query}'")
        
        try:
            result = search_papers(query, 1, True)
            if result["success"]:
                paper = result["papers"][0] if result["papers"] else None
                if paper:
                    print(f"Found paper: {paper['title']}")
                    print(f"Authors: {paper['authors']}")
                    summary = paper.get('summary', 'No summary available')
                    print(f"Summary: {summary[:150]}...")
                else:
                    print("No papers found")
            else:
                print(f"Search failed: {result.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"Error with direct tool usage: {e}")
        
        # Test the assistant with a simple query
        print("\nTesting agent...")
        query = "Find me 1 paper about reinforcement learning"
        print(f"Query: '{query}'")
        
        try:
            response = assistant.run(query)
            print("\nResponse from agent:")
            print(response)
        except Exception as e:
            print(f"Error running agent: {e}")
        
        # Test listing papers
        print("\nTesting listing downloaded papers...")
        try:
            from agents import list_arxiv_papers
            result = list_arxiv_papers(None, None, 10)
            print(f"List result: {result['message']}")
        except Exception as e:
            print(f"Error listing papers: {e}")
    
except ImportError as e:
    print(f"ImportError: {e}")
    print("\nThe agent package might not be installed correctly.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()