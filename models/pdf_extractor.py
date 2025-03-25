#!/usr/bin/env python3
"""
PDF text extraction module for the arXiv Paper Manager.

This module provides functions for extracting text from downloaded PDF files.
"""

import os
from typing import Dict, Optional

from arxiv_tool.config import PDF_SUBDIR


# Use pypdf for PDF text extraction
try:
    from pypdf import PdfReader
    PDF_PARSER_AVAILABLE = True
except ImportError:
    PDF_PARSER_AVAILABLE = False


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text from a PDF file.
    
    Parameters:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF, or None if extraction fails
    """
    if not PDF_PARSER_AVAILABLE:
        return "PDF text extraction not available. Install pypdf with 'pip install pypdf'"
    
    if not os.path.exists(pdf_path):
        return None
    
    try:
        reader = PdfReader(pdf_path)
        text = ""
        
        # Extract text from all pages
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return None


def get_paper_full_content(paper_id: str, max_chars: int = 100000) -> Dict:
    """
    Get the full content of a paper, including metadata and PDF text.
    
    Parameters:
        paper_id (str): The paper ID
        max_chars (int): Maximum characters to extract from the PDF
        
    Returns:
        dict: Dictionary containing both metadata and PDF text
    """
    from arxiv_tool.database import get_paper_details
    from arxiv_tool.models.metadata import parse_metadata_files
    
    # First, get the paper details from the database
    paper_details = get_paper_details(paper_id)
    if not paper_details:
        return {
            "success": False,
            "error": f"Paper with ID {paper_id} not found in database"
        }
    
    # Get the directory where the paper is stored
    directory = paper_details['directory']
    
    # Parse metadata files
    metadata = parse_metadata_files(directory)
    
    # Get the PDF path
    if paper_details.get('id_number'):
        if paper_details.get('version'):
            pdf_filename = f"{paper_details['id_number']}v{paper_details['version']}.pdf"
        else:
            pdf_filename = f"{paper_details['id_number']}.pdf"
    else:
        # Just use the paper_id as filename
        pdf_filename = f"{paper_id}.pdf"
    
    pdf_path = os.path.join(directory, PDF_SUBDIR, pdf_filename)
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        # Try to find any PDF in the directory
        pdf_dir = os.path.join(directory, PDF_SUBDIR)
        if os.path.exists(pdf_dir):
            pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
            if pdf_files:
                pdf_path = os.path.join(pdf_dir, pdf_files[0])
    
    # If we found a PDF, extract its text
    pdf_text = None
    if os.path.exists(pdf_path):
        pdf_text = extract_text_from_pdf(pdf_path)
        
        # Truncate if too long
        if pdf_text and max_chars > 0 and len(pdf_text) > max_chars:
            pdf_text = pdf_text[:max_chars] + f"\n\n[Text truncated to {max_chars} characters]"
    
    # Combine everything into a single result
    result = {
        "success": True,
        "paper_id": paper_id,
        "metadata": metadata,
        "has_pdf_text": pdf_text is not None,
        "pdf_text": pdf_text if pdf_text else "No text could be extracted from the PDF"
    }
    
    return result