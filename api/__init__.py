#!/usr/bin/env python3
"""
arXiv API interaction modules for the arXiv Paper Manager.

This package provides functions for interacting with the arXiv API,
downloading papers, and parsing API responses.
"""

from api.arxiv_client import (
    search_arxiv, save_response_to_file, extract_pdf_url, download_arxiv_pdf,
    search_with_retry, create_entry_xml
)

from api.paper_parser import (
    extract_paper_details_from_xml
)

__all__ = [
    'search_arxiv', 'save_response_to_file', 'extract_pdf_url', 'download_arxiv_pdf',
    'search_with_retry', 'create_entry_xml', 'extract_paper_details_from_xml'
]