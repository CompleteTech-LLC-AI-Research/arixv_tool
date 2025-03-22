#!/usr/bin/env python3
"""
Main script for the arXiv paper download tool.

This script provides the entry point for the tool and handles command-line arguments
to either start the interactive CLI or run specific commands.
"""

import sys
import argparse
from cli import (
    start_interactive_cli, search_paper, process_paper, batch_download_from_file,
    import_pdf_files, fetch_metadata_for_imported_papers, check_for_paper_updates,
    process_existing_directories
)
from db import initialize_db, list_downloaded_papers
from utils import print_papers_table
from arxiv_api import search_with_retry, save_response_to_file, create_entry_xml

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="arXiv Paper Download Tool")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for papers on arXiv")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-l", "--limit", type=int, default=5, help="Maximum number of results (default: 5)")
    search_parser.add_argument("-a", "--auto-download", action="store_true", help="Automatically download all results")
    
    # Batch download command
    batch_parser = subparsers.add_parser("batch", help="Batch download papers from a file")
    batch_parser.add_argument("file", help="File containing paper IDs (one per line)")
    batch_parser.add_argument("-d", "--delay", type=float, default=3, help="Delay between requests in seconds (default: 3)")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import PDF files")
    import_parser.add_argument("directory", help="Directory containing PDF files")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List downloaded papers")
    
    # Fetch metadata command
    fetch_parser = subparsers.add_parser("fetch-metadata", help="Fetch metadata for imported papers")
    
    # Check updates command
    updates_parser = subparsers.add_parser("check-updates", help="Check for paper updates")
    
    # Process existing directories command
    process_parser = subparsers.add_parser("process", help="Process existing directories")
    
    return parser.parse_args()

def main():
    """Main function to handle command line arguments or start the interactive CLI."""
    args = parse_args()
    
    # Initialize the database
    initialize_db()
    
    if args.command == "search":
        results = search_paper(args.query, args.limit, args.auto_download)
        papers = list_downloaded_papers()
        if papers:
            print("\nDownloaded papers:")
            print_papers_table(papers)
    
    elif args.command == "batch":
        result = batch_download_from_file(args.file, args.delay)
        if result['success']:
            print("\nBatch processing complete!")
            print(f"Total papers processed: {result['total']}")
            print(f"Successfully processed: {result['success_count']}")
            print(f"Already in database: {result['already_exists_count']}")
            print(f"Errors: {result['error_count']}")
            
            papers = list_downloaded_papers()
            if papers:
                print("\nDownloaded papers:")
                print_papers_table(papers)
    
    elif args.command == "import":
        result = import_pdf_files(args.directory)
        if result['success']:
            print(f"\nImport complete: {result['successful']} succeeded, {result['failed']} failed")
    
    elif args.command == "list":
        papers = list_downloaded_papers()
        if papers:
            print_papers_table(papers)
    
    elif args.command == "fetch-metadata":
        result = fetch_metadata_for_imported_papers()
        if result['success'] and result.get('total', 0) > 0:
            print(f"\nMetadata retrieval complete:")
            print(f"  Successfully processed: {result['success_count']}")
            print(f"  Errors: {result['error_count']}")
    
    elif args.command == "check-updates":
        result = check_for_paper_updates()
        if result['success']:
            print(f"\nUpdate check complete:")
            print(f"  Papers checked: {result['total']}")
            print(f"  Updates downloaded: {result['updated']}")
            print(f"  No updates needed: {result['skipped']}")
            print(f"  Errors: {result['errors']}")
    
    elif args.command == "process":
        result = process_existing_directories()
        if result['success']:
            print("\nProcessing complete!")
            print(f"Total paper directories processed: {result['total']}")
            print(f"Papers with metadata: {result['with_metadata']}")
            print(f"Papers with PDFs: {result['with_pdf']}")
    
    else:
        # Start the interactive CLI if no command specified
        start_interactive_cli()

if __name__ == "__main__":
    main()