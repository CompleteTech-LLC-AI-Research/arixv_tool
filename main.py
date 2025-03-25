#!/usr/bin/env python3
"""
Main entry point for the arXiv Paper Manager when used as a module.

This module provides the same functionality as the main.py script,
but can be run as a module: python -m main
"""

import sys
import json

from arxiv_tool.cli import (
    parse_args, start_interactive_cli, search_paper, batch_download_from_file,
    import_pdf_files, fetch_metadata_for_imported_papers, check_for_paper_updates,
    process_existing_directories
)
from arxiv_tool.database import initialize_db, list_downloaded_papers
from arxiv_tool.utils import print_papers_table

# Check for SDK metadata support
try:
    from arxiv_tool.models.sdk_metadata import arxiv_search_to_sdk, output_sdk_json
    AGENT_SDK_AVAILABLE = True
except ImportError:
    AGENT_SDK_AVAILABLE = False


def main():
    """Main function to handle command line arguments or start the interactive CLI."""
    args = parse_args()
    
    # Initialize the database
    initialize_db()
    
    # Check if SDK metadata output is requested and available
    sdk_output = getattr(args, 'sdk_metadata', False) and AGENT_SDK_AVAILABLE
    
    if args.command == "search":
        results = search_paper(args.query, args.limit, args.auto_download)
        
        if sdk_output:
            # Output in Agent SDK compatible format
            try:
                sdk_results = arxiv_search_to_sdk(args.query, "", results)
                print(output_sdk_json(sdk_results))
            except Exception as e:
                print(f"Error generating SDK output: {e}")
        else:
            # Standard output
            papers = list_downloaded_papers()
            if papers:
                print("\nDownloaded papers:")
                print_papers_table(papers)
    
    elif args.command == "batch":
        result = batch_download_from_file(args.file, args.delay)
        
        if sdk_output:
            # Output in Agent SDK compatible format
            try:
                from arxiv_tool.database import list_downloaded_papers as db_list_papers
                papers_data = db_list_papers()
                
                # Create a simple result structure
                sdk_result = {
                    "success": result['success'],
                    "total_processed": result['total'],
                    "successfully_processed": result['success_count'],
                    "already_exists": result['already_exists_count'],
                    "errors": result['error_count'],
                    "downloaded_papers": len(papers_data)
                }
                print(json.dumps(sdk_result, indent=2))
            except Exception as e:
                print(f"Error generating SDK output: {e}")
        elif result['success']:
            # Standard output
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
        
        if sdk_output:
            # Output in Agent SDK compatible format
            print(json.dumps(result, indent=2))
        elif result['success']:
            # Standard output
            print(f"\nImport complete: {result['successful']} succeeded, {result['failed']} failed")
    
    elif args.command == "list":
        papers = list_downloaded_papers()
        
        if sdk_output:
            # Output in Agent SDK compatible format
            try:
                papers_list = []
                for paper in papers:
                    paper_id, category, id_number, version, title, authors, downloaded_at, directory, has_metadata, has_pdf = paper
                    papers_list.append({
                        "paper_id": paper_id,
                        "title": title,
                        "authors": authors,
                        "category": category,
                        "id_number": id_number,
                        "version": version,
                        "downloaded_at": str(downloaded_at),
                        "directory": directory,
                        "has_metadata": bool(has_metadata),
                        "has_pdf": bool(has_pdf)
                    })
                print(json.dumps({"total": len(papers_list), "papers": papers_list}, indent=2))
            except Exception as e:
                print(f"Error generating SDK output: {e}")
        elif papers:
            # Standard output
            print_papers_table(papers)
    
    elif args.command == "fetch-metadata":
        result = fetch_metadata_for_imported_papers()
        
        if sdk_output:
            # Output in Agent SDK compatible format
            print(json.dumps(result, indent=2))
        elif result['success'] and result.get('total', 0) > 0:
            # Standard output
            print(f"\nMetadata retrieval complete:")
            print(f"  Successfully processed: {result['success_count']}")
            print(f"  Errors: {result['error_count']}")
    
    elif args.command == "check-updates":
        result = check_for_paper_updates()
        
        if sdk_output:
            # Output in Agent SDK compatible format
            print(json.dumps(result, indent=2))
        elif result['success']:
            # Standard output
            print(f"\nUpdate check complete:")
            print(f"  Papers checked: {result['total']}")
            print(f"  Updates downloaded: {result['updated']}")
            print(f"  No updates needed: {result['skipped']}")
            print(f"  Errors: {result['errors']}")
    
    elif args.command == "process":
        result = process_existing_directories()
        
        if sdk_output:
            # Output in Agent SDK compatible format
            print(json.dumps(result, indent=2))
        elif result['success']:
            # Standard output
            print("\nProcessing complete!")
            print(f"Total paper directories processed: {result['total']}")
            print(f"Papers with metadata: {result['with_metadata']}")
            print(f"Papers with PDFs: {result['with_pdf']}")
    
    else:
        # Start the interactive CLI if no command specified
        start_interactive_cli()


if __name__ == "__main__":
    main()