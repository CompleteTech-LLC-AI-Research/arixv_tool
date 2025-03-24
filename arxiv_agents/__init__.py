"""
ArXiv Research Agents package - A collection of agents for working with arXiv papers.

This package contains specialized agents for searching, downloading, and managing
scientific papers from arXiv.org using the arXiv Paper Manager.
"""

from .arxiv_research_assistant import (
    ArxivResearchAssistant, 
    get_arxiv_assistant, 
    search_arxiv_papers,
    list_arxiv_papers, 
    download_arxiv_papers,
    check_for_paper_updates,
    fetch_paper_metadata,
    search_papers
)

__all__ = [
    'ArxivResearchAssistant',
    'get_arxiv_assistant',
    'search_arxiv_papers',
    'list_arxiv_papers',
    'download_arxiv_papers',
    'check_for_paper_updates',
    'fetch_paper_metadata',
    'search_papers',
]