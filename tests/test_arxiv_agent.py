#!/usr/bin/env python3
"""
Test script for the ArXiv Research Assistant agent.
"""

import os
import sys

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the refactored agent (using our renamed module)
    from arxiv_agents import get_arxiv_assistant
    
    # Import the ArxivTool for direct tool usage
    from agent_wrapper import ArxivTool, ArxivSearchParams
    
    print("Testing ArXiv Research Assistant...")
    
    # Get the singleton instance
    assistant = get_arxiv_assistant("ArXiv Research Expert")
    
    if assistant:
        print(f"Agent created successfully: {assistant.name}")
        
        # First, test direct ArxivTool usage
        print("\nTesting direct ArxivTool usage...")
        arxiv_tool = ArxivTool()
        search_query = "reinforcement learning"
        print(f"Search query: '{search_query}'")
        
        try:
            result = arxiv_tool.search_papers(
                ArxivSearchParams(query=search_query, limit=1, auto_download=True)
            )
            print(f"Search result: {result.message}")
            if result.papers:
                paper = result.papers[0]
                print(f"Found paper: {paper.title}")
                print(f"Authors: {paper.authors}")
                if paper.summary:
                    summary = paper.summary[:100] + "..." if len(paper.summary) > 100 else paper.summary
                    print(f"Summary: {summary}")
        except Exception as e:
            print(f"Error with direct tool usage: {e}")
            import traceback
            traceback.print_exc()
        
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
            import traceback
            traceback.print_exc()
    
except ImportError as e:
    print(f"ImportError: {e}")
    print("\nThe agent package might not be installed correctly.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()