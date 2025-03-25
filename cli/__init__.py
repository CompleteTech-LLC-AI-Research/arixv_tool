#!/usr/bin/env python3
"""
Command-line interface package for the arXiv Paper Manager.

This package provides modules for interacting with the arXiv Paper Manager
through a command-line interface.
"""

from .interactive import start_interactive_cli
from .parser import parse_args
from .commands import (
    search_paper, batch_download_from_file, import_pdf_files,
    fetch_metadata_for_imported_papers, check_for_paper_updates,
    process_existing_directories
)

__all__ = [
    'start_interactive_cli', 'parse_args', 
    'search_paper', 'batch_download_from_file', 'import_pdf_files',
    'fetch_metadata_for_imported_papers', 'check_for_paper_updates',
    'process_existing_directories'
]