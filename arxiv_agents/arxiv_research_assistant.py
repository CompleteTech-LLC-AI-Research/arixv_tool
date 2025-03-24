#!/usr/bin/env python3
"""
ArXiv Research Assistant - An agent for searching and managing arXiv papers.

This module provides a specialized agent for interacting with the arXiv Paper Manager
to search, download, and manage scientific papers from arXiv.org.
"""

import os
import sys
from typing import Dict, List, Any, Optional, Union

# Add parent directory to path to import agent_wrapper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the OpenAI Agents SDK
import agents as openai_agents
from agents import Agent
from agents.run import Runner, RunConfig
from agents.tool import function_tool

# Import the ArxivTool from the agent_wrapper
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agent_wrapper import (
    ArxivTool, ArxivSearchParams, ArxivBatchParams, 
    ArxivListParams, ArxivOperationResult
)


# Define function tools for the agent - removed default values to fix schema validation
@function_tool
def search_arxiv_papers(query: str, limit: int, auto_download: bool) -> Dict[str, Any]:
    """
    Search for scientific papers on arXiv by query.
    
    Parameters
    ----------
    query : str
        The search query for arXiv. Can use special syntax like:
        - Keywords: "quantum computing"
        - Authors: "au:bengio"
        - Category: "cat:cs.AI"
        - Title: "ti:transformer"
        - Combinations: "au:hinton AND cat:cs.LG"
    limit : int
        Maximum number of papers to return (recommended: 5-10)
    auto_download : bool
        Whether to automatically download matching papers (true/false)
        
    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - success: Whether the search was successful
        - message: A description of the result
        - papers: List of papers with metadata (title, authors, summary, etc.)
        - total_papers: Total number of papers found
    """
    # Always use auto_download=True to avoid interactive prompt
    tool = ArxivTool()
    params = ArxivSearchParams(
        query=query,
        limit=limit,
        auto_download=True  # Force auto-download to avoid interactive prompt
    )
    result = tool.search_papers(params)
    
    # Convert to a simple dictionary for the agent
    response = {
        "success": result.success,
        "message": result.message,
        "total_papers": len(result.papers) if result.papers else 0,
        "papers": [paper.dict() for paper in result.papers] if result.papers else []
    }
    
    return response

@function_tool
def list_arxiv_papers(search_term: Optional[str], search_field: Optional[str], limit: int) -> Dict[str, Any]:
    """
    List papers that have been downloaded to the local database.
    
    Parameters
    ----------
    search_term : str
        Term to filter papers by (use null for all papers)
    search_field : str
        Field to search in ('title', 'authors', 'category', 'id') (use null for all fields)
    limit : int
        Maximum number of papers to return (recommended: 100)
        
    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - success: Whether the listing was successful
        - message: A description of the result
        - papers: List of papers with metadata (title, authors, summary, etc.)
        - total_papers: Total number of papers found
    """
    tool = ArxivTool()
    params = ArxivListParams(
        search_term=search_term,
        search_field=search_field,
        limit=limit
    )
    result = tool.list_papers(params)
    
    # Convert to a simple dictionary for the agent
    response = {
        "success": result.success,
        "message": result.message,
        "total_papers": len(result.papers) if result.papers else 0,
        "papers": [paper.dict() for paper in result.papers] if result.papers else []
    }
    
    return response

@function_tool
def download_arxiv_papers(paper_ids: List[str], delay: float) -> Dict[str, Any]:
    """
    Download multiple papers by their arXiv IDs.
    
    Parameters
    ----------
    paper_ids : List[str]
        List of arXiv paper IDs to download (e.g. ["1706.03762", "1312.6114"])
    delay : float
        Delay between requests in seconds (recommended: 3.0)
        
    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - success: Whether the download was successful
        - message: A description of the result
        - stats: Statistics about the download (total, successful, errors)
        - papers: List of downloaded papers with metadata
    """
    tool = ArxivTool()
    params = ArxivBatchParams(
        paper_ids=paper_ids,
        delay=delay
    )
    result = tool.batch_download(params)
    
    # Convert to a simple dictionary for the agent
    response = {
        "success": result.success,
        "message": result.message,
        "stats": result.data if result.data else {},
        "papers": [paper.dict() for paper in result.papers] if result.papers else []
    }
    
    return response

@function_tool
def check_for_paper_updates() -> Dict[str, Any]:
    """
    Check for updates to papers in the database.
    
    This function checks if newer versions of the papers in the database 
    are available on arXiv, and downloads them if they are.
        
    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - success: Whether the operation was successful
        - message: A human-readable message describing the result
        - stats: Statistics about the update check
    """
    tool = ArxivTool()
    result = tool.check_updates()
    
    return {
        "success": result.success,
        "message": result.message,
        "stats": result.data if result.data else {}
    }

@function_tool
def fetch_paper_metadata() -> Dict[str, Any]:
    """
    Fetch metadata for papers that were imported without metadata.
    
    This function searches for papers in the database that have PDFs but no metadata,
    and retrieves the metadata from arXiv.
        
    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - success: Whether the operation was successful
        - message: A human-readable message describing the result
        - stats: Statistics about the metadata retrieval
    """
    tool = ArxivTool()
    result = tool.fetch_metadata()
    
    return {
        "success": result.success,
        "message": result.message,
        "stats": result.data if result.data else {}
    }


class ArxivResearchAssistant:
    """
    A specialized agent for searching and managing arXiv papers.
    
    This class creates and manages an OpenAI-based agent that is configured
    with tools for interacting with the arXiv Paper Manager.
    """
    
    def __init__(self, name: str = "ArXiv Research Assistant"):
        """
        Initialize the ArXiv Research Assistant.
        
        Parameters
        ----------
        name : str, optional
            The name of the agent, default is "ArXiv Research Assistant"
        """
        self.name = name
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        Create an OpenAI Agent with the arXiv tools.
        
        Returns
        -------
        Agent
            An agent configured with the arXiv tools.
        """
        agent = Agent(
            name=self.name,
            instructions="""You are a helpful research assistant that can search for scientific papers on arXiv.
            
            You can help users search for papers by title, author, category, or keywords, and download papers for them.
            You can also list papers that have already been downloaded, check for updates to papers, and more.
            
            Available tools:
            - search_arxiv_papers: Search for papers on arXiv by topic, author, or category
            - list_arxiv_papers: List papers that have been downloaded
            - download_arxiv_papers: Download specific papers by their arXiv IDs
            - check_for_paper_updates: Check for updates to papers in the database
            - fetch_paper_metadata: Fetch metadata for papers that were imported without metadata
            
            When responding about papers, include:
            1. Title and authors
            2. A brief summary of the paper if available
            3. Publication date if available
            4. A link to the PDF if available
            
            IMPORTANT: When using search_arxiv_papers, you MUST specify values for all parameters:
            - query: The search query string
            - limit: An integer (recommended: 5)
            - auto_download: Always use 'true' for this parameter
            
            Be clear, concise, and helpful in your responses.""",
            tools=[
                search_arxiv_papers, 
                list_arxiv_papers, 
                download_arxiv_papers,
                check_for_paper_updates,
                fetch_paper_metadata
            ]
        )
        
        return agent
    
    def run(self, query: str, context: Dict[str, Any] = None) -> str:
        """
        Run the agent with a user query.
        
        Parameters
        ----------
        query : str
            The user's query or request
        context : Dict[str, Any], optional
            Optional context to provide to the agent
            
        Returns
        -------
        str
            The agent's response
        """
        if context is None:
            context = {}
            
        result = Runner.run_sync(
            starting_agent=self.agent,
            input=query,
            context=context
        )
        
        return result.final_output
    
    def run_with_config(self, query: str, context: Dict[str, Any] = None, 
                       run_config: Optional[RunConfig] = None, max_turns: int = 10) -> Any:
        """
        Run the agent with a user query and custom configuration.
        
        Parameters
        ----------
        query : str
            The user's query or request
        context : Dict[str, Any], optional
            Optional context to provide to the agent
        run_config : RunConfig, optional
            Custom run configuration for the agent
        max_turns : int, optional
            Maximum number of agent turns, default is 10
            
        Returns
        -------
        Any
            The complete result object from the agent run
        """
        if context is None:
            context = {}
            
        result = Runner.run_sync(
            starting_agent=self.agent,
            input=query,
            context=context,
            run_config=run_config,
            max_turns=max_turns
        )
        
        return result


# Singleton instance
_instance = None

def get_arxiv_assistant(name: str = "ArXiv Research Assistant") -> ArxivResearchAssistant:
    """
    Get a singleton instance of the ArXiv Research Assistant.
    
    Parameters
    ----------
    name : str, optional
        The name of the agent, default is "ArXiv Research Assistant"
        
    Returns
    -------
    ArxivResearchAssistant
        An instance of the ArXiv Research Assistant
    """
    global _instance
    if _instance is None:
        _instance = ArxivResearchAssistant(name)
    
    return _instance


# For direct tool usage without an agent
def search_papers(query: str, limit: int = 5, auto_download: bool = True) -> Dict[str, Any]:
    """
    Search for papers on arXiv.
    
    This is a direct tool function that doesn't require an agent.
    
    Parameters
    ----------
    query : str
        The search query for arXiv
    limit : int, optional
        Maximum number of papers to return, default is 5
    auto_download : bool, optional
        Whether to automatically download matching papers, default is True
        
    Returns
    -------
    Dict[str, Any]
        A dictionary containing search results
    """
    # Cannot directly call function_tool decorated functions, so we'll implement the same logic
    tool = ArxivTool()
    params = ArxivSearchParams(
        query=query,
        limit=limit,
        auto_download=auto_download
    )
    result = tool.search_papers(params)
    
    # Convert to a simple dictionary
    response = {
        "success": result.success,
        "message": result.message,
        "total_papers": len(result.papers) if result.papers else 0,
        "papers": [paper.dict() for paper in result.papers] if result.papers else []
    }
    
    return response


# For testing
if __name__ == "__main__":
    try:
        # Create an assistant
        assistant = get_arxiv_assistant()
        print(f"Created assistant: {assistant.name}")
        
        # Test direct tool usage with the ArxivTool
        print("\nTesting direct tool usage...")
        result = search_papers("machine learning", 1, True)
        print(f"Found {result['total_papers']} papers")
        
        if result["papers"]:
            paper = result["papers"][0]
            print(f"Found paper: {paper['title']}")
        
        # Run a test query
        print("\nRunning test query through agent...")
        response = assistant.run("Find me 1 paper about quantum computing")
        print("\nResponse from assistant:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()