#!/usr/bin/env python3
"""
Interactive CLI module for the arXiv Paper Manager.

This module provides the interactive command-line interface
for the arXiv Paper Manager.
"""

import os
from typing import Optional

from database import initialize_db, list_downloaded_papers, search_local_papers
from utils import print_papers_table
from cli.commands import (
    search_paper, batch_download_from_file, import_pdf_files,
    fetch_metadata_for_imported_papers, check_for_paper_updates, process_existing_directories
)


def display_menu():
    """Display the main menu and return the user's choice."""
    print("\nOptions:")
    print("1. Search for papers on arXiv")
    print("2. List downloaded papers")
    print("3. Search local papers")
    print("4. Import PDF files")
    print("5. Fetch metadata for imported papers")
    print("6. Check for paper updates")
    print("7. Batch download from file")
    print("8. Process existing directories")
    print("9. Exit")
    
    while True:
        choice = input("\nEnter choice (1-9): ")
        if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return choice
        print("Invalid choice. Please enter a number between 1 and 9.")


def start_interactive_cli():
    """Start the interactive command-line interface."""
    print("ArXiv Paper Download Tool")
    print("========================")
    
    # Initialize the database
    initialize_db()
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            query = input("Enter search query: ")
            limit = input("Enter maximum results (default: 5): ")
            try:
                limit = int(limit) if limit.strip() else 5
            except ValueError:
                print(f"Invalid input: '{limit}'. Using default: 5.")
                limit = 5
                
            auto_download = input("Automatically download all results? (y/n, default: n): ").lower() == 'y'
            search_paper(query, limit, auto_download)
            
            # List all downloaded papers after search
            papers = list_downloaded_papers()
            if papers:
                print_papers_table(papers)
                
        elif choice == '2':
            papers = list_downloaded_papers()
            if papers:
                print_papers_table(papers)
            
        elif choice == '3':
            print("\nSearch local papers by:")
            print("1. Title")
            print("2. Author")
            print("3. Category")
            print("4. Paper ID")
            search_type = input("\nEnter choice (1-4): ")
            
            field_map = {
                '1': 'title',
                '2': 'authors',
                '3': 'category',
                '4': 'id'
            }
            
            if search_type in field_map:
                search_term = input(f"Enter {field_map[search_type]} to search for: ")
                papers = search_local_papers(search_term, field_map[search_type])
                if papers:
                    print_papers_table(papers)
            else:
                print("Invalid choice.")
                
        elif choice == '4':
            directory = input("Enter directory path containing PDF files: ")
            if os.path.exists(directory) and os.path.isdir(directory):
                result = import_pdf_files(directory)
                if result['success']:
                    print(f"\nImport complete: {result['successful']} succeeded, {result['failed']} failed")
            else:
                print(f"Directory '{directory}' does not exist or is not a directory.")
                
        elif choice == '5':
            result = fetch_metadata_for_imported_papers()
            if result['success'] and result.get('total', 0) > 0:
                print(f"\nMetadata retrieval complete:")
                print(f"  Successfully processed: {result['success_count']}")
                print(f"  Errors: {result['error_count']}")
                
                # Show updated papers
                papers = list_downloaded_papers()
                if papers:
                    print("\nUpdated papers:")
                    print_papers_table(papers)
                
        elif choice == '6':
            result = check_for_paper_updates()
            if result['success']:
                print(f"\nUpdate check complete:")
                print(f"  Papers checked: {result['total']}")
                print(f"  Updates downloaded: {result['updated']}")
                print(f"  No updates needed: {result['skipped']}")
                print(f"  Errors: {result['errors']}")
                
                if result['updated'] > 0:
                    # Show updated papers
                    papers = list_downloaded_papers()
                    if papers:
                        print("\nUpdated papers:")
                        print_papers_table(papers)
                
        elif choice == '7':
            file_path = input("Enter path to file containing paper IDs (one per line): ")
            if os.path.exists(file_path) and os.path.isfile(file_path):
                delay = input("Enter delay between requests in seconds (default: 3): ")
                try:
                    delay = float(delay) if delay.strip() else 3
                except ValueError:
                    print(f"Invalid input: '{delay}'. Using default: 3.")
                    delay = 3
                
                result = batch_download_from_file(file_path, delay)
                if result['success']:
                    print("\nBatch processing complete!")
                    print(f"Total papers processed: {result['total']}")
                    print(f"Successfully processed: {result['success_count']}")
                    print(f"Already in database: {result['already_exists_count']}")
                    print(f"Errors: {result['error_count']}")
                    
                    # List all downloaded papers
                    papers = list_downloaded_papers()
                    if papers:
                        print("\nListing all papers in database:")
                        print_papers_table(papers)
            else:
                print(f"File '{file_path}' does not exist or is not a file.")
                
        elif choice == '8':
            result = process_existing_directories()
            if result['success']:
                print("\nProcessing complete!")
                print(f"Total paper directories processed: {result['total']}")
                print(f"Papers with metadata: {result['with_metadata']}")
                print(f"Papers with PDFs: {result['with_pdf']}")
                
                # List all downloaded papers
                papers = list_downloaded_papers()
                if papers:
                    print("\nListing all papers in database:")
                    print_papers_table(papers)
                
        elif choice == '9':
            print("Exiting. Goodbye!")
            break