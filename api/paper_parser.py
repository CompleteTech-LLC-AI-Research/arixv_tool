#!/usr/bin/env python3
"""
Paper parsing module for the arXiv Paper Manager.

This module provides functions to parse and extract metadata from arXiv API responses.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Optional, Any, List, Union

from config import XML_NAMESPACES
from utils import extract_paper_id, get_simplified_paper_id, sanitize_filename
from api.arxiv_client import extract_pdf_url


def extract_summary(entry: ET.Element, ns: Dict[str, str]) -> str:
    """Extract summary from entry"""
    summary_elem = entry.find('atom:summary', ns)
    return summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""


def extract_published_date(entry: ET.Element, ns: Dict[str, str]) -> str:
    """Extract published date from entry"""
    published_elem = entry.find('atom:published', ns)
    return published_elem.text.strip() if published_elem is not None and published_elem.text else ""


def extract_updated_date(entry: ET.Element, ns: Dict[str, str]) -> str:
    """Extract updated date from entry"""
    updated_elem = entry.find('atom:updated', ns)
    return updated_elem.text.strip() if updated_elem is not None and updated_elem.text else ""


def extract_doi(entry: ET.Element, ns: Dict[str, str]) -> str:
    """Extract DOI from entry"""
    doi_elem = entry.find('arxiv:doi', ns)
    return doi_elem.text.strip() if doi_elem is not None and doi_elem.text else ""


def extract_journal_ref(entry: ET.Element, ns: Dict[str, str]) -> str:
    """Extract journal reference from entry"""
    journal_ref_elem = entry.find('arxiv:journal_ref', ns)
    return journal_ref_elem.text.strip() if journal_ref_elem is not None and journal_ref_elem.text else ""


def extract_comment(entry: ET.Element, ns: Dict[str, str]) -> str:
    """Extract comment from entry"""
    comment_elem = entry.find('arxiv:comment', ns)
    return comment_elem.text.strip() if comment_elem is not None and comment_elem.text else ""


def extract_primary_category(entry: ET.Element, ns: Dict[str, str]) -> str:
    """Extract primary category from entry"""
    primary_cat_elem = entry.find('arxiv:primary_category', ns)
    if primary_cat_elem is not None:
        category = primary_cat_elem.attrib.get('term', '')
        return category
    
    # If no primary category found, try to find the first regular category
    categories = extract_categories(entry, ns)
    if categories:
        return categories[0]
        
    return ""


def extract_categories(entry: ET.Element, ns: Dict[str, str]) -> List[str]:
    """Extract all categories from entry"""
    categories = []
    for cat_elem in entry.findall('atom:category', ns):
        category = cat_elem.attrib.get('term', '')
        if category:
            categories.append(category)
    return categories


def extract_links(entry: ET.Element, ns: Dict[str, str]) -> List[Dict[str, str]]:
    """Extract all links from entry"""
    links = []
    for link in entry.findall('atom:link', ns):
        link_data = {
            'rel': link.attrib.get('rel', ''),
            'href': link.attrib.get('href', ''),
            'title': link.attrib.get('title', ''),
            'type': link.attrib.get('type', '')
        }
        links.append(link_data)
    return links


def extract_paper_details_from_xml(xml_response: str) -> Optional[Dict[str, Any]]:
    """
    Extract key details about a paper from the arXiv XML response.
    
    Parameters:
        xml_response (str): The XML response from arXiv API
        
    Returns:
        dict: A dictionary containing paper details or None if extraction fails
    """
    try:
        ns = XML_NAMESPACES
        root = ET.fromstring(xml_response)
        entry = root.find('atom:entry', ns)
        
        if entry is None:
            print("No entry found in the XML response.")
            return None
        
        # Extract paper ID
        id_elem = entry.find('atom:id', ns)
        if id_elem is None or not id_elem.text:
            print("No paper ID found in the entry.")
            return None
        paper_id = id_elem.text.strip()
        
        # Extract title
        title_elem = entry.find('atom:title', ns)
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Unknown Title"
        
        # Extract authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name_elem = author.find('atom:name', ns)
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text.strip())
        
        # Get paper_id from URL
        paper_id = extract_paper_id(paper_id)
        
        # Get ID parts
        from utils import extract_paper_id_parts
        parts = extract_paper_id_parts(paper_id)
        
        # Get simplified ID and create safe directory name
        # Only add version suffix if it's explicitly present in the original ID
        if 'v' in paper_id:
            simple_id = parts['id_number'] + 'v' + parts['version']
        else:
            simple_id = parts['id_number']
        
        safe_paper_id = sanitize_filename(simple_id)
        
        return {
            'paper_id': paper_id,
            'category': parts['category'],
            'id_number': parts['id_number'],
            'version': parts['version'],
            'safe_paper_id': safe_paper_id,
            'title': title,
            'authors': ', '.join(authors),
            'pdf_url': extract_pdf_url(xml_response),
            'summary': extract_summary(entry, ns),
            'published': extract_published_date(entry, ns),
            'updated': extract_updated_date(entry, ns),
            'doi': extract_doi(entry, ns),
            'journal_ref': extract_journal_ref(entry, ns),
            'comment': extract_comment(entry, ns),
            'primary_category': extract_primary_category(entry, ns),
            'categories': extract_categories(entry, ns),
            'links': extract_links(entry, ns)
        }
    except Exception as e:
        print(f"Error extracting paper details: {e}")
        return None