#!/usr/bin/env python3
"""
Data models and handlers for the arXiv Paper Manager.

This package provides modules for handling various types of data:
- Metadata extraction and parsing
- PDF text extraction
- SDK metadata conversion for AI agent integration
"""

from arxiv_tool.models.metadata import extract_and_save_metadata, parse_metadata_files
from arxiv_tool.models.pdf_extractor import extract_text_from_pdf, get_paper_full_content
from arxiv_tool.models.sdk_metadata import arxiv_search_to_sdk, output_sdk_json

try:
    from arxiv_tool.models.sdk_metadata import ArxivPaper, ArxivSearchResults
    PYDANTIC_MODELS_AVAILABLE = True
except:
    PYDANTIC_MODELS_AVAILABLE = False

__all__ = [
    'extract_and_save_metadata', 'parse_metadata_files',
    'extract_text_from_pdf', 'get_paper_full_content',
    'arxiv_search_to_sdk', 'output_sdk_json'
]

if PYDANTIC_MODELS_AVAILABLE:
    __all__.extend(['ArxivPaper', 'ArxivSearchResults'])