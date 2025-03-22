#!/usr/bin/env python3
"""
Utility functions for the arXiv paper download tool.

This module provides common helper functions used across other modules including:
- Path handling
- File operations
- Paper ID parsing
- Text formatting
"""

import os
import re

def sanitize_filename(name):
    """
    Replace characters that are not alphanumeric, dash, underscore, or dot with underscores.
    This helps in creating a safe directory name.
    
    Parameters:
        name (str): The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    return re.sub(r'[^\w\-_\.]', '_', name)

def get_simplified_paper_id(paper_id):
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

def extract_paper_id_parts(paper_id):
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

def extract_paper_id(url):
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

def ensure_dir_exists(directory):
    """
    Create a directory if it does not already exist.
    
    Parameters:
        directory (str): The directory path to create
        
    Returns:
        bool: True if the directory exists or was created successfully
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False

def save_to_file(content, file_path):
    """
    Save content to a file, creating parent directories if needed.
    
    Parameters:
        content (str): The content to write to the file
        file_path (str): The full path to the file
        
    Returns:
        bool: True if the file was written successfully
    """
    try:
        directory = os.path.dirname(file_path)
        ensure_dir_exists(directory)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def is_valid_arxiv_id(dirname):
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

def format_paper_table_row(paper, truncate_title=37):
    """
    Format a paper record for table display.
    
    Parameters:
        paper (tuple): The paper record from the database
        truncate_title (int): Length to truncate the title to (0 for no truncation)
        
    Returns:
        dict: Dictionary with formatted fields for display
    """
    paper_id, category, id_number, version, title, authors, downloaded_at, directory, has_metadata, has_pdf = paper
    
    # Format category field
    category_display = category if category else "-"
    
    # Format version field (handle None or empty version)
    version_display = version if version else "-"
    
    # Truncate title if too long
    if title and truncate_title > 0 and len(title) > truncate_title:
        title_display = title[:truncate_title] + "..."
    else:
        title_display = title
    
    # Format metadata and PDF status
    metadata_status = "✓" if has_metadata else "✗"
    pdf_status = "✓" if has_pdf else "✗"
    
    # Format date
    date_display = downloaded_at[:19] if downloaded_at else ""
    
    return {
        'id_number': id_number,
        'version': version_display,
        'category': category_display,
        'title': title_display,
        'date': date_display,
        'metadata': metadata_status,
        'pdf': pdf_status
    }

def print_papers_table(papers, header=True):
    """
    Print a formatted table of papers.
    
    Parameters:
        papers (list): List of paper records from the database
        header (bool): Whether to print the table header
    """
    if not papers:
        print("No papers found.")
        return
    
    if header:
        print(f"\nTotal papers: {len(papers)}\n")
        print(f"{'ID Number':<12} {'V':<2} {'Category':<12} {'Title':<40} {'Downloaded':<20} {'Metadata':<10} {'PDF':<10}")
        print("-" * 110)
    
    for paper in papers:
        paper_data = format_paper_table_row(paper)
        print(f"{paper_data['id_number']:<12} {paper_data['version']:<2} {paper_data['category']:<12} "
              f"{paper_data['title']:<40} {paper_data['date']:<20} {paper_data['metadata']:<10} {paper_data['pdf']:<10}")
    
    print()