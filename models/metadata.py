#!/usr/bin/env python3
"""
Metadata handling module for the arXiv Paper Manager.

This module provides functions for parsing, extracting, and managing metadata
for arXiv papers.
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any

from config import METADATA_SUBDIR, XML_NAMESPACES
from utils import (
    extract_paper_id, get_simplified_paper_id, sanitize_filename, 
    ensure_dir_exists, save_to_file
)


def extract_and_save_metadata(xml_response: str, paper_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract metadata from arXiv API response and save it to files.
    
    Parameters:
        xml_response (str): The XML response from arXiv API
        paper_dir (str, optional): Directory where metadata will be saved.
                                 If None, a directory will be created based on paper ID.
    
    Returns:
        dict: A dictionary containing the extracted metadata and success status
    """
    # Parse the XML
    try:
        root = ET.fromstring(xml_response)
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return {'success': False, 'error': f"XML parsing error: {e}"}
    
    # Get the paper entry
    ns = XML_NAMESPACES
    entry = root.find('atom:entry', ns)
    if entry is None:
        return {'success': False, 'error': "No entry found in XML"}
    
    # Extract paper id from <id>
    id_elem = entry.find('atom:id', ns)
    if id_elem is None or not id_elem.text:
        return {'success': False, 'error': "No paper ID found in entry"}
    
    paper_url = id_elem.text.strip()
    paper_id = extract_paper_id(paper_url)
    
    # Use simplified ID (without category prefix)
    simple_id = get_simplified_paper_id(paper_id)
    safe_paper_id = sanitize_filename(simple_id)
    
    # Create paper directory if not provided
    if paper_dir is None:
        paper_dir = safe_paper_id
    
    # Create metadata subdirectory
    metadata_dir = os.path.join(paper_dir, METADATA_SUBDIR)
    ensure_dir_exists(metadata_dir)
    
    # Dictionary to store all extracted metadata
    metadata = {
        'paper_id': paper_id,
        'safe_paper_id': safe_paper_id,
        'success': True,
        'files_saved': []
    }
    
    # Save the paper URL as id.txt
    id_file = os.path.join(metadata_dir, 'id.txt')
    save_to_file(paper_url, id_file)
    metadata['files_saved'].append(id_file)
    
    # Extract and save all relevant metadata fields
    fields_to_extract = [
        ('updated', 'atom:updated'),
        ('published', 'atom:published'),
        ('title', 'atom:title'),
        ('summary', 'atom:summary'),
        ('doi', 'arxiv:doi'),
        ('journal_ref', 'arxiv:journal_ref'),
        ('comment', 'arxiv:comment')
    ]
    
    for field_name, xpath in fields_to_extract:
        elem = entry.find(xpath, ns)
        if elem is not None and elem.text:
            content = elem.text.strip()
            file_path = os.path.join(metadata_dir, f"{field_name}.txt")
            save_to_file(content, file_path)
            metadata[field_name] = content
            metadata['files_saved'].append(file_path)
    
    # Process authors: gather each author with their affiliation (if provided)
    authors = []
    author_names = []
    for author in entry.findall('atom:author', ns):
        name_elem = author.find('atom:name', ns)
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else "Unknown"
        author_names.append(name)
        
        affiliation_elem = author.find('arxiv:affiliation', ns)
        affiliation = affiliation_elem.text.strip() if affiliation_elem is not None and affiliation_elem.text else "No affiliation"
        authors.append(f"{name} ({affiliation})")
    
    if authors:
        file_path = os.path.join(metadata_dir, "authors.txt")
        save_to_file("\n".join(authors), file_path)
        metadata['authors'] = author_names
        metadata['authors_with_affiliation'] = authors
        metadata['files_saved'].append(file_path)
    
    # Process and save all link elements
    links = []
    for link in entry.findall('atom:link', ns):
        # Retrieve attributes such as rel, href, title, and type
        rel = link.attrib.get('rel', '')
        href = link.attrib.get('href', '')
        title_attr = link.attrib.get('title', '')
        type_attr = link.attrib.get('type', '')
        links.append(f"title: {title_attr}, rel: {rel}, type: {type_attr}, href: {href}")
        
        # If this is the PDF link, save it separately
        if title_attr == 'pdf' or type_attr == 'application/pdf':
            metadata['pdf_url'] = href
    
    if links:
        file_path = os.path.join(metadata_dir, "links.txt")
        save_to_file("\n".join(links), file_path)
        metadata['links'] = links
        metadata['files_saved'].append(file_path)
    
    # Save primary category
    primary_cat_elem = entry.find('arxiv:primary_category', ns)
    if primary_cat_elem is not None:
        primary_cat = primary_cat_elem.attrib.get('term', '')
        file_path = os.path.join(metadata_dir, "primary_category.txt")
        save_to_file(primary_cat, file_path)
        metadata['primary_category'] = primary_cat
        metadata['files_saved'].append(file_path)
    
    # Save category
    cat_elem = entry.find('atom:category', ns)
    if cat_elem is not None:
        cat_term = cat_elem.attrib.get('term', '')
        file_path = os.path.join(metadata_dir, "category.txt")
        save_to_file(cat_term, file_path)
        metadata['category'] = cat_term
        metadata['files_saved'].append(file_path)
    
    print(f"Metadata files have been saved in the directory: {metadata_dir}")
    return metadata


def parse_metadata_files(paper_dir: str) -> Dict[str, Any]:
    """
    Read metadata files from a paper directory and return as a dictionary.
    
    Parameters:
        paper_dir (str): Path to the paper directory
        
    Returns:
        dict: Dictionary of metadata values read from files
    """
    metadata_dir = os.path.join(paper_dir, METADATA_SUBDIR)
    if not os.path.exists(metadata_dir):
        return {'success': False, 'error': f"Metadata directory does not exist: {metadata_dir}"}
    
    metadata = {'paper_dir': paper_dir, 'success': True}
    
    # List of metadata files to read
    metadata_files = [
        'id.txt', 'title.txt', 'authors.txt', 'summary.txt', 
        'published.txt', 'updated.txt', 'doi.txt', 'journal_ref.txt',
        'comment.txt', 'primary_category.txt', 'category.txt', 'links.txt'
    ]
    
    for filename in metadata_files:
        file_path = os.path.join(metadata_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    field_name = os.path.splitext(filename)[0]
                    metadata[field_name] = content
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    # Extract paper_id from directory name if not found in metadata
    if 'paper_id' not in metadata and 'id' in metadata:
        metadata['paper_id'] = extract_paper_id(metadata['id'])
    elif 'paper_id' not in metadata:
        metadata['paper_id'] = os.path.basename(paper_dir)
    
    return metadata