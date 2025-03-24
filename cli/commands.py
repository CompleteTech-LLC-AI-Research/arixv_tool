#!/usr/bin/env python3
"""
Command implementation module for the arXiv Paper Manager.

This module provides functions for executing various commands:
- Searching arXiv
- Processing papers
- Managing local papers
"""

import os
import time
import glob
import shutil
import sqlite3
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple, Union

from config import METADATA_SUBDIR, PDF_SUBDIR, DEFAULT_DELAY, XML_NAMESPACES
from database import (
    initialize_db, paper_exists, record_paper_download, update_paper_status,
    list_downloaded_papers, search_local_papers
)
from api import (
    search_arxiv, save_response_to_file, extract_pdf_url, download_arxiv_pdf, 
    extract_paper_details_from_xml, search_with_retry, create_entry_xml
)
from models import extract_and_save_metadata
from utils import (
    extract_paper_id_parts, get_simplified_paper_id, sanitize_filename,
    ensure_dir_exists, is_valid_arxiv_id, print_papers_table, extract_paper_id
)


def process_paper(xml_response: str) -> Dict[str, Any]:
    """
    Process a single paper from its XML representation.

    This handles extracting details, checking if it exists in the database,
    and downloading metadata and PDF if needed.

    Parameters:
        xml_response (str): The XML response containing the paper entry
        
    Returns:
        dict: Result of the processing with status information
    """
    # Save the XML response to a temporary file
    saved_path = save_response_to_file(xml_response, "arxiv_search_result", directory=".", file_type="xml")
    
    # Extract paper details from the XML
    paper_details = extract_paper_details_from_xml(xml_response)
    if not paper_details:
        return {
            'success': False,
            'error': "Failed to extract paper details from XML response."
        }
    
    paper_id = paper_details['paper_id']
    safe_paper_id = paper_details['safe_paper_id']
    title = paper_details['title']
    authors = paper_details['authors']
    pdf_url = paper_details['pdf_url']
    primary_category = paper_details.get('primary_category', '')
    
    # Check if paper has already been downloaded
    if paper_exists(paper_id):
        return {
            'success': True,
            'status': 'already_exists',
            'message': f"Paper '{title}' ({paper_id}) has already been downloaded to {safe_paper_id}/ directory.",
            'paper_id': paper_id,
            'safe_paper_id': safe_paper_id,
            'title': title
        }
    
    print(f"\nDownloading paper: {title}")
    print(f"Primary Category: {primary_category}")
    
    # Create the initial database record (will be updated as we complete steps)
    record_paper_download(
        paper_id=paper_id,
        title=title,
        authors=authors,
        directory=safe_paper_id,
        has_metadata=False,
        has_pdf=False,
        category=primary_category
    )
    
    result = {
        'success': True,
        'paper_id': paper_id,
        'safe_paper_id': safe_paper_id,
        'title': title,
        'authors': authors,
        'metadata_status': False,
        'pdf_status': False
    }
    
    # Extract and save metadata
    try:
        metadata_result = extract_and_save_metadata(xml_response)
        if metadata_result['success']:
            update_paper_status(paper_id, has_metadata=True)
            result['metadata_status'] = True
            print(f"✓ Metadata extracted successfully")
        else:
            print(f"✗ Error extracting metadata: {metadata_result.get('error', 'Unknown error')}")
            update_paper_status(paper_id, has_metadata=False)
    except Exception as e:
        print(f"✗ Error extracting metadata: {e}")
        update_paper_status(paper_id, has_metadata=False)
    
    # Download the PDF
    if pdf_url:
        # Create the directory if it doesn't already exist
        if not os.path.exists(safe_paper_id):
            os.makedirs(safe_paper_id)
            
        # Create pdf subdirectory
        pdf_dir = os.path.join(safe_paper_id, PDF_SUBDIR)
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        try:
            # Download the PDF into the pdf subdirectory
            pdf_path = download_arxiv_pdf(pdf_url, directory=pdf_dir)
            print(f"✓ PDF downloaded to: {pdf_path}")
            update_paper_status(paper_id, has_pdf=True)
            result['pdf_status'] = True
            result['pdf_path'] = pdf_path
        except Exception as e:
            print(f"✗ Error downloading PDF: {e}")
            update_paper_status(paper_id, has_pdf=False)
    else:
        print("✗ No PDF URL found for this paper")
        update_paper_status(paper_id, has_pdf=False)
        
    print(f"\nPaper successfully processed: {title}")
    print(f"Files saved to: {safe_paper_id}/")
    
    return result


def search_paper(query: str, limit: int = 5, auto_download: bool = False) -> List[Dict[str, Any]]:
    """
    Search for papers and handle downloading if requested.
    
    Parameters:
        query (str): The search query string
        limit (int): Maximum number of results to return
        auto_download (bool): Whether to automatically download all results
        
    Returns:
        list: List of paper details if auto_download is True, otherwise None
    """
    # Initialize the database
    initialize_db()
    
    print(f"Searching arXiv for: '{query}' (limit: {limit})")
    xml_response = search_with_retry(query, max_results=limit)
    
    if not xml_response:
        print("Failed to get response from arXiv.")
        return []
    
    # Save the response for debugging
    save_response_to_file(xml_response, "arxiv_search_result", directory=".", file_type="xml")
    
    # Parse all entries in the response
    root = ET.fromstring(xml_response)
    entries = root.findall('atom:entry', XML_NAMESPACES)
    
    if not entries:
        print("No papers found matching your query.")
        return []
    
    print(f"\nFound {len(entries)} papers:\n")
    
    if auto_download:
        print("Processing all papers automatically...\n")
        results = []
        
        for i, entry in enumerate(entries):
            # Create a single-entry XML
            selected_xml = create_entry_xml(entry)
            
            # Extract ID for logging
            id_elem = entry.find('atom:id', XML_NAMESPACES)
            title_elem = entry.find('atom:title', XML_NAMESPACES)
            
            if id_elem is not None and title_elem is not None:
                paper_id = extract_paper_id(id_elem.text.strip())
                title = title_elem.text.strip()
                print(f"Processing paper {i+1}/{len(entries)}: {paper_id}")
                print(f"Title: {title}")
                
                # Process the paper
                try:
                    result = process_paper(selected_xml)
                    results.append(result)
                    if result['success']:
                        print(f"✓ Successfully processed paper {paper_id}")
                    else:
                        print(f"✗ Error processing paper {paper_id}: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"✗ Error processing paper {paper_id}: {e}")
                
                # Sleep to avoid overwhelming the arXiv API
                if i < len(entries) - 1:  # No need to sleep after the last paper
                    print(f"Waiting {DEFAULT_DELAY} seconds before next request...")
                    time.sleep(DEFAULT_DELAY)
        
        return results
    else:
        # Interactive mode with user selection
        print(f"{'#':<3} {'Paper ID':<25} {'Title':<50} {'Authors':<30}")
        print("-" * 108)
        
        # Process each entry
        for i, entry in enumerate(entries):
            # Extract basic information for display
            id_elem = entry.find('atom:id', XML_NAMESPACES)
            title_elem = entry.find('atom:title', XML_NAMESPACES)
            
            if id_elem is None or title_elem is None:
                continue
                
            paper_id = extract_paper_id(id_elem.text.strip())
            title = title_elem.text.strip()
            
            # Get first author for display
            authors = []
            for author in entry.findall('atom:author', XML_NAMESPACES):
                name_elem = author.find('atom:name', XML_NAMESPACES)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())
            
            author_str = authors[0] + " et al." if len(authors) > 1 else authors[0] if authors else "Unknown"
            
            # Truncate title and authors if too long
            if len(title) > 47:
                title = title[:47] + "..."
            if len(author_str) > 27:
                author_str = author_str[:27] + "..."
            
            print(f"{i+1:<3} {paper_id:<25} {title:<50} {author_str:<30}")
        
        # Ask user which paper to download
        while True:
            choice = input("\nEnter paper number to download (or 'q' to quit): ")
            if choice.lower() == 'q':
                return []
            
            try:
                choice = int(choice)
                if 1 <= choice <= len(entries):
                    # Process the selected entry by creating a single-entry XML
                    selected_entry = entries[choice-1]
                    selected_xml = create_entry_xml(selected_entry)
                    
                    # Use the regular flow to process this paper
                    return [process_paper(selected_xml)]
                else:
                    print(f"Please enter a number between 1 and {len(entries)}")
            except ValueError:
                print("Please enter a valid number")


def batch_download_from_file(file_path: str, delay: float = DEFAULT_DELAY) -> Dict[str, Any]:
    """
    Download papers listed in a file.
    
    Parameters:
        file_path (str): Path to the file containing paper IDs (one per line)
        delay (int): Delay between requests in seconds
        
    Returns:
        dict: Summary of download results
    """
    # Initialize the database
    initialize_db()
    
    # Read paper IDs from file
    try:
        with open(file_path, 'r') as file:
            paper_ids = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return {'success': False, 'error': 'File not found'}
    
    print(f"Found {len(paper_ids)} paper IDs to process.")
    
    # Process each paper ID
    success_count = 0
    error_count = 0
    already_exists_count = 0
    
    for i, paper_id in enumerate(paper_ids):
        print(f"\nProcessing paper {i+1}/{len(paper_ids)}: {paper_id}")
        
        # Check if paper already exists in database
        if paper_exists(paper_id):
            print(f"Paper {paper_id} already exists in database. Skipping.")
            already_exists_count += 1
            continue
        
        try:
            # Get arXiv XML for the paper
            xml_response = search_with_retry(f"id:{paper_id}", max_results=1)
            
            if not xml_response:
                print(f"Failed to get response for paper {paper_id}.")
                error_count += 1
                continue
            
            # Process the paper
            result = process_paper(xml_response)
            
            if result['success']:
                success_count += 1
            else:
                error_count += 1
                print(f"Error processing paper {paper_id}: {result.get('error', 'Unknown error')}")
            
            # Sleep to avoid overwhelming the arXiv API
            if i < len(paper_ids) - 1:  # No need to sleep after the last paper
                print(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"Error processing paper {paper_id}: {e}")
            error_count += 1
            
            # Sleep a bit longer after an error
            print(f"Waiting {delay*2} seconds after error...")
            time.sleep(delay * 2)
    
    # Return summary
    summary = {
        'success': True,
        'total': len(paper_ids),
        'success_count': success_count,
        'already_exists_count': already_exists_count,
        'error_count': error_count
    }
    
    return summary


def import_pdf_files(directory: str) -> Dict[str, Any]:
    """
    Import PDF files from a directory into the database.
    
    Parameters:
        directory (str): Directory containing PDF files
        
    Returns:
        dict: Summary of import results
    """
    # Initialize the database
    initialize_db()
    
    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in directory: {directory}")
        return {'success': False, 'error': 'No PDF files found'}
    
    print(f"Found {len(pdf_files)} PDF files in {directory}")
    print("Importing files...")
    
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        # Extract the ID from the filename
        paper_id = os.path.splitext(pdf_file)[0]
        
        # Extract parts of the ID
        parts = extract_paper_id_parts(paper_id)
        
        # Create directory path
        if 'v' in paper_id:
            safe_paper_id = parts['id_number'] + 'v' + parts['version']
        else:
            safe_paper_id = parts['id_number']
        
        safe_paper_id = sanitize_filename(safe_paper_id)
        
        try:
            # Create directories
            if not os.path.exists(safe_paper_id):
                os.makedirs(safe_paper_id)
            
            pdf_dir = os.path.join(safe_paper_id, PDF_SUBDIR)
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
            
            # Copy the PDF file
            source_path = os.path.join(directory, pdf_file)
            dest_path = os.path.join(pdf_dir, pdf_file)
            shutil.copy2(source_path, dest_path)
            
            # Record in database
            record_paper_download(
                paper_id=paper_id,
                title=f"Imported: {paper_id}",
                authors="",
                directory=safe_paper_id,
                has_metadata=False,
                has_pdf=True
            )
            
            successful += 1
            print(f"✓ Imported: {pdf_file}")
        except Exception as e:
            failed += 1
            print(f"✗ Failed to import {pdf_file}: {e}")
    
    # Return summary
    summary = {
        'success': True,
        'total': len(pdf_files),
        'successful': successful,
        'failed': failed
    }
    
    return summary


def fetch_metadata_for_imported_papers() -> Dict[str, Any]:
    """
    Retrieve metadata for papers that were imported as PDFs without metadata.
    
    Returns:
        dict: Summary of metadata retrieval results
    """
    # Initialize the database
    initialize_db()
    
    # Query papers with PDFs but no metadata
    import sqlite3
    conn = sqlite3.connect('arxiv_papers.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT paper_id, directory FROM papers
            WHERE has_pdf = 1 AND has_metadata = 0
        ''')
        
        papers = cursor.fetchall()
    finally:
        conn.close()
    
    if not papers:
        print("No papers found that need metadata retrieval.")
        return {'success': True, 'papers_processed': 0}
    
    print(f"Found {len(papers)} papers without metadata:")
    
    success_count = 0
    error_count = 0
    
    for i, (paper_id, directory) in enumerate(papers):
        print(f"\n[{i+1}/{len(papers)}] Processing: {paper_id}")
        
        try:
            # Search arXiv by paper ID
            print(f"  Fetching metadata from arXiv...")
            xml_response = search_with_retry(f"id:{paper_id}", max_results=1)
            
            if not xml_response:
                print(f"  ✗ Failed to get response for paper {paper_id}.")
                error_count += 1
                continue
            
            # Save the XML response
            saved_path = save_response_to_file(xml_response, "arxiv_search_result", directory=".", file_type="xml")
            
            # Extract paper details
            paper_details = extract_paper_details_from_xml(xml_response)
            if not paper_details:
                print(f"  ✗ Failed to extract paper details.")
                error_count += 1
                continue
            
            # Extract metadata
            metadata_result = extract_and_save_metadata(xml_response)
            
            if not metadata_result['success']:
                print(f"  ✗ Error extracting metadata: {metadata_result.get('error', 'Unknown error')}")
                error_count += 1
                continue
            
            # Update database
            update_paper_status(paper_id, has_metadata=True)
            
            # If we have title, authors, and primary category from metadata, update those too
            if paper_details['title'] and paper_details['authors']:
                primary_category = paper_details.get('primary_category', '')
                conn = sqlite3.connect('arxiv_papers.db')
                cursor = conn.cursor()
                try:
                    cursor.execute('''
                        UPDATE papers
                        SET title = ?, authors = ?, category = ?
                        WHERE paper_id = ?
                    ''', (paper_details['title'], paper_details['authors'], primary_category, paper_id))
                    conn.commit()
                finally:
                    conn.close()
            
            print(f"  ✓ Metadata retrieved successfully for {paper_id}")
            success_count += 1
            
            # Add a delay to avoid overwhelming the API
            if i < len(papers) - 1:
                print("  Waiting 3 seconds before next request...")
                time.sleep(3)
                
        except Exception as e:
            print(f"  ✗ Error retrieving metadata for {paper_id}: {e}")
            error_count += 1
    
    # Return summary
    summary = {
        'success': True,
        'total': len(papers),
        'success_count': success_count,
        'error_count': error_count
    }
    
    return summary


def check_for_paper_updates() -> Dict[str, Any]:
    """
    Check for newer versions of papers and update them if available.
    
    Returns:
        dict: Summary of update check results
    """
    # Initialize the database
    initialize_db()
    
    import sqlite3
    conn = sqlite3.connect('arxiv_papers.db')
    cursor = conn.cursor()
    
    try:
        # Check if the table has the updated schema
        cursor.execute("PRAGMA table_info(papers)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        has_new_schema = 'category' in column_names and 'id_number' in column_names and 'version' in column_names
        
        if not has_new_schema:
            print("This function requires the updated database schema.")
            return {'success': False, 'error': 'Database schema not updated'}
        
        # Get all papers from the database
        cursor.execute('''
            SELECT paper_id, id_number, version FROM papers
            ORDER BY downloaded_at DESC
        ''')
        
        papers = cursor.fetchall()
    finally:
        conn.close()
    
    if not papers:
        print("No papers found in the database.")
        return {'success': True, 'papers_checked': 0}
    
    print(f"Checking {len(papers)} papers for updates...")
    
    updated_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, (paper_id, id_number, version) in enumerate(papers):
        print(f"\n[{i+1}/{len(papers)}] Checking: {paper_id}")
        
        try:
            # For papers without a version number in the ID, we can't check for updates
            if not version or version == '1':
                # For papers where we don't have a version in the ID (like '2101.00001')
                # we need to search by the base ID number to see if newer versions exist
                search_id = id_number
            else:
                # For papers with an explicit version, we strip the version to search
                search_id = id_number
            
            print(f"  Searching for updates to {search_id}...")
            
            # Search arXiv for the paper by ID number (without version)
            xml_response = search_with_retry(f"id_list:{search_id}", max_results=5)
            
            if not xml_response:
                print(f"  ✗ Failed to get response for paper {search_id}.")
                error_count += 1
                continue
            
            # Parse the XML to find all versions
            root = ET.fromstring(xml_response)
            entries = root.findall('atom:entry', XML_NAMESPACES)
            
            if not entries:
                print(f"  No entries found for {search_id}")
                skipped_count += 1
                continue
            
            # Find the latest version
            latest_version = None
            latest_entry_xml = None
            latest_paper_id = None
            
            for entry in entries:
                id_elem = entry.find('atom:id', XML_NAMESPACES)
                if id_elem is None or not id_elem.text:
                    continue
                
                entry_paper_id = extract_paper_id(id_elem.text.strip())
                entry_parts = extract_paper_id_parts(entry_paper_id)
                
                # Only consider entries with the same ID number
                if entry_parts['id_number'] != id_number:
                    continue
                
                if latest_version is None or int(entry_parts['version']) > int(latest_version):
                    latest_version = entry_parts['version']
                    latest_paper_id = entry_paper_id
                    
                    # Create a new XML containing just this entry
                    latest_entry_xml = create_entry_xml(entry)
            
            if latest_version is None:
                print(f"  Could not determine latest version for {search_id}")
                skipped_count += 1
                continue
            
            # Check if we already have the latest version
            if version and int(latest_version) <= int(version):
                print(f"  Paper is already at the latest version (v{version})")
                skipped_count += 1
                continue
            
            # We found a newer version - download it
            print(f"  Found newer version: v{latest_version} (current: v{version})")
            print(f"  Downloading update: {latest_paper_id}")
            
            # Process the paper
            result = process_paper(latest_entry_xml)
            
            if result['success']:
                updated_count += 1
                print(f"  ✓ Successfully updated to version {latest_version}")
            else:
                error_count += 1
                print(f"  ✗ Error updating to version {latest_version}: {result.get('error', 'Unknown error')}")
            
            # Add a delay to avoid overwhelming the API
            if i < len(papers) - 1:
                print("  Waiting 3 seconds before next paper...")
                time.sleep(3)
            
        except Exception as e:
            print(f"  ✗ Error checking for updates: {e}")
            error_count += 1
            
            # Add a longer delay after an error
            if i < len(papers) - 1:
                print("  Waiting 5 seconds after error...")
                time.sleep(5)
    
    # Return summary
    summary = {
        'success': True,
        'total': len(papers),
        'updated': updated_count,
        'skipped': skipped_count,
        'errors': error_count
    }
    
    return summary


def process_existing_directories() -> Dict[str, Any]:
    """
    Process existing paper directories and add them to the database.
    
    Returns:
        dict: Summary of processing results
    """
    # Initialize the database
    print("Initializing database...")
    initialize_db()
    
    # Find all potential paper directories (exclude special directories)
    special_dirs = ['test_imports', 'test_imports_mixed', 'papers']
    all_dirs = [d for d in glob.glob('*/') if os.path.basename(d.rstrip('/')) not in special_dirs]
    paper_dirs = []
    
    # Filter for directories that look like paper directories
    for d in all_dirs:
        base_dir = d.rstrip('/')
        dir_name = os.path.basename(base_dir)
        
        # Check if the directory name matches an arXiv ID pattern
        if is_valid_arxiv_id(dir_name):
            # Additional check: directory must have metadata or pdf subdirectory
            if os.path.exists(os.path.join(base_dir, METADATA_SUBDIR)) or os.path.exists(os.path.join(base_dir, PDF_SUBDIR)):
                paper_dirs.append(base_dir)
    
    print(f"Found {len(paper_dirs)} paper directories")
    
    # Process each paper directory
    success_metadata = 0
    success_pdf = 0
    
    for paper_dir in paper_dirs:
        paper_id = os.path.basename(paper_dir)
        
        # Check if metadata and PDF directories exist
        has_metadata = os.path.exists(os.path.join(paper_dir, METADATA_SUBDIR)) and len(os.listdir(os.path.join(paper_dir, METADATA_SUBDIR))) > 0
        pdf_dir = os.path.join(paper_dir, PDF_SUBDIR)
        has_pdf = os.path.exists(pdf_dir) and len(os.listdir(pdf_dir)) > 0
        
        # Try to extract title, authors, and category if metadata exists
        title = None
        authors = None
        category = None
        
        if has_metadata:
            # Extract title
            title_path = os.path.join(paper_dir, METADATA_SUBDIR, 'title.txt')
            if os.path.exists(title_path):
                with open(title_path, 'r', encoding='utf-8') as f:
                    title = f.read().strip()
            
            # Extract authors
            authors_path = os.path.join(paper_dir, METADATA_SUBDIR, 'authors.txt')
            if os.path.exists(authors_path):
                with open(authors_path, 'r', encoding='utf-8') as f:
                    authors = f.read().strip()
            
            # Extract category
            category_path = os.path.join(paper_dir, METADATA_SUBDIR, 'primary_category.txt')
            if os.path.exists(category_path):
                with open(category_path, 'r', encoding='utf-8') as f:
                    category = f.read().strip()
            # Fall back to category.txt if primary_category.txt doesn't exist
            elif os.path.exists(os.path.join(paper_dir, METADATA_SUBDIR, 'category.txt')):
                with open(os.path.join(paper_dir, METADATA_SUBDIR, 'category.txt'), 'r', encoding='utf-8') as f:
                    category = f.read().strip()
        
        if title is None:
            title = f"Paper: {paper_id}"
        if authors is None:
            authors = ""
        
        # Parse the paper ID
        parts = extract_paper_id_parts(paper_id)
        
        # Update the category in parts if we found it in metadata
        if category:
            parts['category'] = category
        
        print(f"Processing {paper_id}:")
        print(f"  Title: {title}")
        print(f"  Category: {category if category else '-'}")
        print(f"  Has metadata: {has_metadata}")
        print(f"  Has PDF: {has_pdf}")
        
        # Record the paper in the database with the updated category
        if record_paper_download(
            paper_id=paper_id,
            title=title,
            authors=authors, 
            directory=paper_id,
            has_metadata=has_metadata,
            has_pdf=has_pdf,
            category=parts['category']  # Use the category we found
        ):
            print(f"  ✓ Added to database")
        else:
            print(f"  ✗ Failed to add to database")
        
        if has_metadata:
            success_metadata += 1
        if has_pdf:
            success_pdf += 1
        print("  ------------------")
    
    # Return summary
    summary = {
        'success': True,
        'total': len(paper_dirs),
        'with_metadata': success_metadata,
        'with_pdf': success_pdf
    }
    
    return summary