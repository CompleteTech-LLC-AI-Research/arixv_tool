#!/usr/bin/env python3
"""
arXiv API interaction module for the paper download tool.

This module provides functions for:
- Querying the arXiv API
- Downloading PDFs
- Extracting paper information from API responses
"""

import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import time

# Import utility functions
from utils import extract_paper_id, get_simplified_paper_id, sanitize_filename

def search_arxiv(search_query, start=0, max_results=10):
    """
    Query the arXiv API for articles matching the specified search criteria.

    Sends a GET request to the arXiv API endpoint using the provided parameters and returns
    the raw XML response containing metadata for the matching articles.

    Parameters:
        search_query (str): The search query string used to filter arXiv articles 
                          (e.g., "all:electron", "cat:physics.gen-ph").
        start (int, optional): The zero-based index of the first result to return. Defaults to 0.
        max_results (int, optional): The maximum number of results to retrieve. Defaults to 10.

    Returns:
        str: A string containing the XML response from the arXiv API.

    Raises:
        urllib.error.URLError: If there is an issue with the network connection or the API endpoint.
    """
    base_url = 'http://export.arxiv.org/api/query?'
    params = {
        'search_query': search_query,
        'start': start,
        'max_results': max_results
    }
    query_params = urllib.parse.urlencode(params)
    full_url = base_url + query_params

    with urllib.request.urlopen(full_url) as response:
        result = response.read().decode('utf-8')
    
    return result

def save_response_to_file(response, save_filename, directory=None, file_type='xml'):
    """
    Save a text response to a file with the specified name, directory, and file type.

    If the provided filename does not end with the correct extension, it is appended automatically.

    Parameters:
        response (str): The textual content to be saved.
        save_filename (str): The base filename (without extension) to use when saving the content.
        directory (str, optional): The directory where the file will be saved. If None, the current working directory is used.
        file_type (str, optional): The file extension/type (e.g., "xml", "txt"). Defaults to "xml".

    Returns:
        str: The full file path to the saved file.
    """
    if not save_filename.endswith('.' + file_type):
        save_filename = f"{save_filename}.{file_type}"
    
    full_path = os.path.join(directory, save_filename) if directory else save_filename
    
    from utils import save_to_file
    save_to_file(response, full_path)
    
    return full_path

def extract_pdf_url(xml_response):
    """
    Parse the arXiv API XML response to extract the first available PDF URL.

    The function searches for a <link> element with either a title attribute equal to "pdf"
    or a MIME type attribute of "application/pdf" and returns its href value.

    Parameters:
        xml_response (str): The XML response string from the arXiv API.

    Returns:
        str: The URL of the PDF if found; otherwise, returns None.
    """
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(xml_response)
    
    for entry in root.findall('atom:entry', ns):
        for link in entry.findall('atom:link', ns):
            if link.attrib.get('title') == 'pdf' or link.attrib.get('type') == 'application/pdf':
                return link.attrib.get('href')
    return None

def download_arxiv_pdf(pdf_url, save_filename=None, directory=None):
    """
    Download a PDF from the specified URL and save it locally.

    If no save_filename is provided, the function defaults to using the paper's identifier,
    extracted from the last segment of the PDF URL, as the filename.

    Parameters:
        pdf_url (str): The URL from which to download the PDF.
        save_filename (str, optional): The desired base filename (without extension) for the PDF.
                                     If None, the paper ID (last segment of the URL) is used.
        directory (str, optional): The directory where the PDF file will be saved. Defaults to the current working directory if None.

    Returns:
        str: The full file path to the saved PDF.

    Raises:
        urllib.error.URLError: If there is an issue downloading the PDF from the provided URL.
    """
    if save_filename is None:
        # Default to the paper ID derived from the last segment of the URL
        save_filename = pdf_url.rstrip('/').split('/')[-1]
    
    file_type = "pdf"
    if not save_filename.endswith('.' + file_type):
        save_filename = f"{save_filename}.{file_type}"
    
    full_path = os.path.join(directory, save_filename) if directory else save_filename
    
    # Ensure directory exists
    from utils import ensure_dir_exists
    if directory:
        ensure_dir_exists(directory)
    
    with urllib.request.urlopen(pdf_url) as response:
        pdf_data = response.read()
    
    with open(full_path, 'wb') as file:
        file.write(pdf_data)
    
    return full_path

def extract_paper_details_from_xml(xml_response):
    """
    Extract key details about a paper from the arXiv XML response.
    
    Parameters:
        xml_response (str): The XML response from arXiv API
        
    Returns:
        dict: A dictionary containing paper details or None if extraction fails
    """
    try:
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
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

def extract_summary(entry, ns):
    """Extract summary from entry"""
    summary_elem = entry.find('atom:summary', ns)
    return summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""

def extract_published_date(entry, ns):
    """Extract published date from entry"""
    published_elem = entry.find('atom:published', ns)
    return published_elem.text.strip() if published_elem is not None and published_elem.text else ""

def extract_updated_date(entry, ns):
    """Extract updated date from entry"""
    updated_elem = entry.find('atom:updated', ns)
    return updated_elem.text.strip() if updated_elem is not None and updated_elem.text else ""

def extract_doi(entry, ns):
    """Extract DOI from entry"""
    doi_elem = entry.find('arxiv:doi', ns)
    return doi_elem.text.strip() if doi_elem is not None and doi_elem.text else ""

def extract_journal_ref(entry, ns):
    """Extract journal reference from entry"""
    journal_ref_elem = entry.find('arxiv:journal_ref', ns)
    return journal_ref_elem.text.strip() if journal_ref_elem is not None and journal_ref_elem.text else ""

def extract_comment(entry, ns):
    """Extract comment from entry"""
    comment_elem = entry.find('arxiv:comment', ns)
    return comment_elem.text.strip() if comment_elem is not None and comment_elem.text else ""

def extract_primary_category(entry, ns):
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

def extract_categories(entry, ns):
    """Extract all categories from entry"""
    categories = []
    for cat_elem in entry.findall('atom:category', ns):
        category = cat_elem.attrib.get('term', '')
        if category:
            categories.append(category)
    return categories

def extract_links(entry, ns):
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

def create_entry_xml(entry):
    """
    Create a standalone XML for a single entry.
    
    Parameters:
        entry (Element): The entry element from arXiv API response
        
    Returns:
        str: XML string containing only this entry
    """
    new_root = ET.Element('{http://www.w3.org/2005/Atom}feed')
    new_root.append(entry)
    return ET.tostring(new_root, encoding='utf-8').decode('utf-8')

def search_with_retry(search_query, max_results=10, retry_count=3, delay=3):
    """
    Search arXiv with retry capability in case of network errors.
    
    Parameters:
        search_query (str): The search query string
        max_results (int): Maximum number of results to retrieve
        retry_count (int): Number of retry attempts
        delay (int): Delay between retries in seconds
        
    Returns:
        str: The XML response from arXiv or None if all retries fail
    """
    for attempt in range(retry_count):
        try:
            return search_arxiv(search_query, max_results=max_results)
        except Exception as e:
            if attempt < retry_count - 1:
                print(f"Error searching arXiv (attempt {attempt+1}/{retry_count}): {e}")
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to search arXiv after {retry_count} attempts: {e}")
                return None