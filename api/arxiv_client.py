#!/usr/bin/env python3
"""
arXiv API client module for the arXiv Paper Manager.

This module provides functions to interact with the arXiv API:
- Search for papers
- Download PDFs
- Parse API responses
"""

import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Union, Any

from arxiv_tool.config import ARXIV_API_BASE_URL, XML_NAMESPACES
from arxiv_tool.utils import (
    extract_paper_id, get_simplified_paper_id, sanitize_filename, 
    ensure_dir_exists, save_to_file
)


def search_arxiv(search_query: str, start: int = 0, max_results: int = 10) -> str:
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
    params = {
        'search_query': search_query,
        'start': start,
        'max_results': max_results
    }
    query_params = urllib.parse.urlencode(params)
    full_url = f"{ARXIV_API_BASE_URL}?{query_params}"

    with urllib.request.urlopen(full_url) as response:
        result = response.read().decode('utf-8')
    
    return result


def save_response_to_file(response: str, save_filename: str, directory: Optional[str] = None, file_type: str = 'xml') -> str:
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
    
    save_to_file(response, full_path)
    
    return full_path


def extract_pdf_url(xml_response: str) -> Optional[str]:
    """
    Parse the arXiv API XML response to extract the first available PDF URL.

    The function searches for a <link> element with either a title attribute equal to "pdf"
    or a MIME type attribute of "application/pdf" and returns its href value.

    Parameters:
        xml_response (str): The XML response string from the arXiv API.

    Returns:
        str: The URL of the PDF if found; otherwise, returns None.
    """
    ns = XML_NAMESPACES
    root = ET.fromstring(xml_response)
    
    for entry in root.findall('atom:entry', ns):
        for link in entry.findall('atom:link', ns):
            if link.attrib.get('title') == 'pdf' or link.attrib.get('type') == 'application/pdf':
                return link.attrib.get('href')
    return None


def download_arxiv_pdf(pdf_url: str, save_filename: Optional[str] = None, directory: Optional[str] = None) -> str:
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
    if directory:
        ensure_dir_exists(directory)
    
    with urllib.request.urlopen(pdf_url) as response:
        pdf_data = response.read()
    
    with open(full_path, 'wb') as file:
        file.write(pdf_data)
    
    return full_path


def search_with_retry(search_query: str, max_results: int = 10, retry_count: int = 3, delay: int = 3) -> Optional[str]:
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


def create_entry_xml(entry: ET.Element) -> str:
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