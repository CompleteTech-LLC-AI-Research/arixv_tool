#!/usr/bin/env python3
"""
Command-line argument parser for the arXiv Paper Manager.

This module defines the CLI argument parser using argparse.
"""

import argparse
from typing import Dict, Any


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="arXiv Paper Download Tool")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for papers on arXiv")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-l", "--limit", type=int, default=5, help="Maximum number of results (default: 5)")
    search_parser.add_argument("-a", "--auto-download", action="store_true", help="Automatically download all results")
    search_parser.add_argument("--sdk-metadata", action="store_true", help="Output results in Agent SDK compatible metadata format")
    
    # Batch download command
    batch_parser = subparsers.add_parser("batch", help="Batch download papers from a file")
    batch_parser.add_argument("file", help="File containing paper IDs (one per line)")
    batch_parser.add_argument("-d", "--delay", type=float, default=3, help="Delay between requests in seconds (default: 3)")
    batch_parser.add_argument("--sdk-metadata", action="store_true", help="Output results in Agent SDK compatible metadata format")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import PDF files")
    import_parser.add_argument("directory", help="Directory containing PDF files")
    import_parser.add_argument("--sdk-metadata", action="store_true", help="Output results in Agent SDK compatible metadata format")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List downloaded papers")
    list_parser.add_argument("--sdk-metadata", action="store_true", help="Output results in Agent SDK compatible metadata format")
    
    # Fetch metadata command
    fetch_parser = subparsers.add_parser("fetch-metadata", help="Fetch metadata for imported papers")
    fetch_parser.add_argument("--sdk-metadata", action="store_true", help="Output results in Agent SDK compatible metadata format")
    
    # Check updates command
    updates_parser = subparsers.add_parser("check-updates", help="Check for paper updates")
    updates_parser.add_argument("--sdk-metadata", action="store_true", help="Output results in Agent SDK compatible metadata format")
    
    # Process existing directories command
    process_parser = subparsers.add_parser("process", help="Process existing directories")
    process_parser.add_argument("--sdk-metadata", action="store_true", help="Output results in Agent SDK compatible metadata format")
    
    return parser.parse_args()