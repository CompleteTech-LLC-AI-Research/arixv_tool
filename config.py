#!/usr/bin/env python3
"""
Configuration module for the arXiv Paper Manager.

This module contains constants and configuration settings used throughout the application.
"""

import os

# Database settings
DB_FILE = 'arxiv_papers.db'

# API settings
ARXIV_API_BASE_URL = 'http://export.arxiv.org/api/query'

# Request settings
DEFAULT_DELAY = 3  # seconds
MAX_RESULTS_DEFAULT = 5

# File paths and directory structure
PDF_SUBDIR = 'pdf'
METADATA_SUBDIR = 'metadata'

# Metadata files
METADATA_FILES = {
    'id.txt': 'id',
    'title.txt': 'title',
    'authors.txt': 'authors',
    'summary.txt': 'summary',
    'published.txt': 'published',
    'updated.txt': 'updated',
    'doi.txt': 'doi',
    'journal_ref.txt': 'journal_ref',
    'comment.txt': 'comment',
    'primary_category.txt': 'primary_category',
    'category.txt': 'category',
    'links.txt': 'links'
}

# XML namespace mappings
XML_NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
    'arxiv': 'http://arxiv.org/schemas/atom'
}