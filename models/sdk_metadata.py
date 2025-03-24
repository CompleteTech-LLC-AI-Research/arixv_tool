#!/usr/bin/env python3
"""
SDK metadata module for the arXiv Paper Manager.

This module provides functions for converting arXiv paper data to formats
compatible with the OpenAI Agent SDK.
"""

import json
import os
from typing import List, Optional, Dict, Any, Union

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("Warning: Pydantic not available. SDK metadata features disabled.")
    # Create a minimal BaseModel for type hints
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def dict(self):
            return vars(self)

    # Create a minimal Field for type hints
    def Field(*args, **kwargs):
        return None


# Define models only if Pydantic is available
if PYDANTIC_AVAILABLE:
    class ArxivPaper(BaseModel):
        """Model representing an arXiv paper for Agent SDK compatibility."""
        paper_id: str = Field(..., description="The arXiv ID of the paper")
        title: str = Field(..., description="The title of the paper")
        authors: str = Field(..., description="Comma-separated list of authors")
        summary: Optional[str] = Field(None, description="Abstract of the paper")
        categories: Optional[List[str]] = Field(None, description="arXiv categories")
        primary_category: Optional[str] = Field(None, description="Primary arXiv category")
        pdf_url: Optional[str] = Field(None, description="URL to the PDF")
        published: Optional[str] = Field(None, description="Publication date")
        local_directory: Optional[str] = Field(None, description="Local directory where files are stored")

    class ArxivSearchResults(BaseModel):
        """Model representing search results for Agent SDK compatibility."""
        query: str = Field(..., description="The search query used")
        total_results: int = Field(..., description="Number of results found")
        papers: List[ArxivPaper] = Field(..., description="List of papers in the search results")
else:
    # Dummy classes for type hints if Pydantic is not available
    class ArxivPaper(BaseModel):
        pass

    class ArxivSearchResults(BaseModel):
        pass


def read_metadata_files(paper_id: str, directory: str) -> Dict[str, Any]:
    """
    Read metadata files from the paper directory.
    
    Parameters:
        paper_id (str): The paper ID
        directory (str): The paper directory
        
    Returns:
        dict: Dictionary containing metadata values
    """
    import os
    from config import METADATA_SUBDIR
    
    metadata_dir = os.path.join(directory, METADATA_SUBDIR)
    if not os.path.exists(metadata_dir):
        return {}
    
    metadata = {}
    
    # List of metadata files to check
    metadata_files = {
        'title.txt': 'title',
        'authors.txt': 'authors',
        'summary.txt': 'summary',
        'category.txt': 'category',
        'primary_category.txt': 'primary_category',
        'published.txt': 'published',
        'updated.txt': 'updated'
    }
    
    for filename, field_name in metadata_files.items():
        file_path = os.path.join(metadata_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    metadata[field_name] = content
            except Exception:
                # If there's an error reading the file, just skip it
                pass
    
    # Get PDF URL from links.txt if available
    links_file = os.path.join(metadata_dir, 'links.txt')
    if os.path.exists(links_file):
        try:
            with open(links_file, 'r', encoding='utf-8') as f:
                links_content = f.read()
                for line in links_content.splitlines():
                    if 'pdf' in line and 'href:' in line:
                        pdf_url = line.split('href:')[-1].strip()
                        metadata['pdf_url'] = pdf_url
                        break
        except Exception:
            pass
    
    return metadata


def arxiv_search_to_sdk(query: str, xml_response: str, results: List[Dict[str, Any]]) -> ArxivSearchResults:
    """
    Convert arXiv search results to OpenAI Agent SDK compatible format.
    
    Parameters:
        query (str): The original search query
        xml_response (str): The XML response from arXiv API
        results (list): The processed results from the search
        
    Returns:
        ArxivSearchResults: A structured representation of the search results
    """
    if not PYDANTIC_AVAILABLE:
        print("Warning: Pydantic not available. SDK metadata conversion disabled.")
        return None
    
    papers = []
    
    for result in results:
        if not result.get('success', False):
            continue
        
        paper_id = result.get('paper_id', '')
        directory = result.get('safe_paper_id', '')
        
        # First use the result details
        paper_data = {
            'paper_id': paper_id,
            'title': result.get('title', ''),
            'authors': result.get('authors', ''),
            'summary': result.get('summary', None),
            'categories': [result.get('category', '')] if result.get('category') else None,
            'primary_category': result.get('primary_category', None),
            'pdf_url': result.get('pdf_url', None),
            'published': result.get('published', None),
            'local_directory': directory
        }
        
        # Then read metadata from files to fill in any missing values
        if directory:
            metadata = read_metadata_files(paper_id, directory)
            
            # Update paper data with metadata
            for key, value in metadata.items():
                # Only update if the value is currently empty
                if not paper_data.get(key) and value:
                    if key == 'category':
                        if not paper_data['categories']:
                            paper_data['categories'] = [value]
                    else:
                        paper_data[key] = value
        
        # Create the paper object
        paper = ArxivPaper(
            paper_id=paper_data['paper_id'],
            title=paper_data['title'],
            authors=paper_data['authors'],
            summary=paper_data['summary'],
            categories=paper_data['categories'],
            primary_category=paper_data['primary_category'],
            pdf_url=paper_data['pdf_url'],
            published=paper_data['published'],
            local_directory=paper_data['local_directory']
        )
        papers.append(paper)
    
    # Create the search results object
    search_results = ArxivSearchResults(
        query=query,
        total_results=len(papers),
        papers=papers
    )
    
    return search_results


def output_sdk_json(search_results: ArxivSearchResults) -> str:
    """
    Output the search results as JSON in a format compatible with OpenAI Agent SDK.
    
    Parameters:
        search_results (ArxivSearchResults): The structured search results
        
    Returns:
        str: JSON string representation of the search results
    """
    if not PYDANTIC_AVAILABLE:
        print("Warning: Pydantic not available. JSON output disabled.")
        return "{}"
    
    return json.dumps(search_results.dict(), indent=2)