#!/usr/bin/env python3
"""
Database package for the arXiv Paper Manager.

This package provides database operations for managing arXiv papers.
"""

from database.db_manager import (
    initialize_db, record_paper_download, update_paper_status, paper_exists,
    search_local_papers, list_downloaded_papers, get_paper_details, delete_paper
)

__all__ = [
    'initialize_db', 'record_paper_download', 'update_paper_status', 'paper_exists',
    'search_local_papers', 'list_downloaded_papers', 'get_paper_details', 'delete_paper'
]