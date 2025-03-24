#!/usr/bin/env python3
"""
Paper ID utility functions for the arXiv Paper Manager.

This module provides functions for parsing and manipulating arXiv paper IDs.
"""

import re
from typing import Dict, Optional


def extract_paper_id(url: str) -> str:
    """
    Extract the paper id from the URL.
    For a URL like 'http://arxiv.org/abs/cond-mat/0102536v1',
    it returns 'cond-mat/0102536v1'.
    
    Parameters:
        url (str): The URL containing the paper ID
        
    Returns:
        str: The extracted paper ID
    """
    if '/abs/' in url:
        return url.split('/abs/')[-1]
    return url.rsplit('/', 1)[-1]


def get_simplified_paper_id(paper_id: str) -> str:
    """
    Extracts a simplified paper ID without the category prefix.
    
    For a paper ID like 'cond-mat/0102536v1', returns '0102536v1'.
    For a paper ID without a category prefix, returns the ID unchanged.
    
    Parameters:
        paper_id (str): The full paper ID, potentially with a category prefix.
        
    Returns:
        str: The simplified paper ID without the category prefix.
    """
    if '/' in paper_id:
        return paper_id.split('/')[-1]
    return paper_id


def extract_paper_id_parts(paper_id: str) -> Dict[str, Optional[str]]:
    """
    Extract the different parts of a paper ID.
    
    For a paper ID like 'cond-mat/0102536v1', extracts:
    - category: 'cond-mat'
    - id_number: '0102536'
    - version: '1'
    
    For a paper ID like '1909.03550v1', extracts:
    - category: None
    - id_number: '1909.03550'
    - version: '1'
    
    For a paper ID without explicit version like 'cond-mat/0102536' or '1909.03550', 
    it treats it as version 1.
    
    Also handles alternative formats like 'math.GT_0512630' or 'cs_0303006v1'.
    
    Parameters:
        paper_id (str): The paper ID to parse
        
    Returns:
        dict: A dictionary with keys 'category', 'id_number', and 'version'
    """
    # Strip the .pdf extension if present
    if paper_id.lower().endswith('.pdf'):
        paper_id = paper_id[:-4]
    
    # Initialize result dictionary
    result = {
        'category': None,
        'id_number': None,
        'version': None
    }
    
    # Handle format like 'math.GT_0512630' or 'cs_0303006v1'
    if '_' in paper_id:
        parts = paper_id.split('_', 1)
        result['category'] = parts[0]
        id_with_version = parts[1]
    
    # Extract category if present with slash format
    elif '/' in paper_id:
        result['category'], id_with_version = paper_id.split('/', 1)
    else:
        id_with_version = paper_id
    
    # Extract version if present
    if 'v' in id_with_version and any(c.isdigit() for c in id_with_version.split('v')[-1]):
        id_parts = id_with_version.split('v')
        result['id_number'] = id_parts[0]
        result['version'] = id_parts[1] if len(id_parts) > 1 else '1'
    else:
        # If no version is present, or if 'v' is part of the ID but not followed by digits
        result['id_number'] = id_with_version
        result['version'] = '1'  # Default version
    
    return result


def is_valid_arxiv_id(dirname: str) -> bool:
    """
    Check if a directory name matches the pattern of an arXiv ID.
    
    Valid patterns include:
    - YYMM.NNNNN(vN) format (e.g., 2101.00001v1)
    - category/YYMMNNN(vN) format (e.g., cond-mat/0102536v1)
    
    Parameters:
        dirname (str): The directory name to check
        
    Returns:
        bool: True if the directory name matches an arXiv ID pattern
    """
    # Modern arXiv ID pattern (YYMM.NNNNN)
    modern_pattern = re.compile(r'^\d{4}\.\d{4,5}v?\d*$')
    
    # Old arXiv ID pattern (category/YYMMNNN)
    old_pattern = re.compile(r'^[a-z\-\.]+\/\d{7}v?\d*$')
    
    # Another format for older papers
    alt_pattern = re.compile(r'^[a-z\.]+\_\d{7}v?\d*$')
    
    return bool(modern_pattern.match(dirname) or 
               old_pattern.match(dirname) or 
               alt_pattern.match(dirname))