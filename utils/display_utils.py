#!/usr/bin/env python3
"""
Display utility functions for the arXiv Paper Manager.

This module provides functions for formatting and displaying data to the user.
"""

from typing import List, Dict, Any, Tuple


def format_paper_table_row(paper: Tuple, truncate_title: int = 37) -> Dict[str, str]:
    """
    Format a paper record for table display.
    
    Parameters:
        paper (tuple): The paper record from the database
        truncate_title (int): Length to truncate the title to (0 for no truncation)
        
    Returns:
        dict: Dictionary with formatted fields for display
    """
    paper_id, category, id_number, version, title, authors, downloaded_at, directory, has_metadata, has_pdf = paper
    
    # Format category field
    category_display = category if category else "-"
    
    # Format version field (handle None or empty version)
    version_display = version if version else "-"
    
    # Truncate title if too long
    if title and truncate_title > 0 and len(title) > truncate_title:
        title_display = title[:truncate_title] + "..."
    else:
        title_display = title
    
    # Format metadata and PDF status
    metadata_status = "✓" if has_metadata else "✗"
    pdf_status = "✓" if has_pdf else "✗"
    
    # Format date
    date_display = downloaded_at[:19] if downloaded_at else ""
    
    return {
        'id_number': id_number,
        'version': version_display,
        'category': category_display,
        'title': title_display,
        'date': date_display,
        'metadata': metadata_status,
        'pdf': pdf_status
    }


def print_papers_table(papers: List[Tuple], header: bool = True) -> None:
    """
    Print a formatted table of papers.
    
    Parameters:
        papers (list): List of paper records from the database
        header (bool): Whether to print the table header
    """
    if not papers:
        print("No papers found.")
        return
    
    if header:
        print(f"\nTotal papers: {len(papers)}\n")
        print(f"{'ID Number':<12} {'V':<2} {'Category':<12} {'Title':<40} {'Downloaded':<20} {'Metadata':<10} {'PDF':<10}")
        print("-" * 110)
    
    for paper in papers:
        paper_data = format_paper_table_row(paper)
        print(f"{paper_data['id_number']:<12} {paper_data['version']:<2} {paper_data['category']:<12} "
              f"{paper_data['title']:<40} {paper_data['date']:<20} {paper_data['metadata']:<10} {paper_data['pdf']:<10}")
    
    print()