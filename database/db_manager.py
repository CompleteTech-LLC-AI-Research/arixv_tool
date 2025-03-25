#!/usr/bin/env python3
"""
Database operations module for the arXiv Paper Manager.

This module provides functions for database management:
- Initialization
- Migration
- Record management
- Paper status tracking
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Union

from arxiv_tool.config import DB_FILE
from arxiv_tool.utils import extract_paper_id_parts, get_simplified_paper_id, sanitize_filename


def initialize_db() -> bool:
    """
    Initialize the SQLite database for tracking downloaded papers.
    
    Creates a table to store information about downloaded papers including:
    - paper_id: The full arXiv ID (e.g., 'cond-mat/0102536v1')
    - category: The paper category (e.g., 'cond-mat')
    - id_number: The paper's number identifier (e.g., '0102536')
    - version: The paper version (e.g., '1')
    - title: The paper title
    - authors: The paper authors (comma-separated)
    - downloaded_at: Timestamp of when the paper was downloaded
    - directory: The directory where the paper files are stored
    - has_metadata: Whether the metadata files were successfully extracted
    - has_pdf: Whether the PDF was successfully downloaded
    
    Returns:
        bool: True if initialization was successful
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if the old table structure exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if we need to migrate the table
            cursor.execute("PRAGMA table_info(papers)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'category' not in column_names or 'id_number' not in column_names or 'version' not in column_names:
                print("Migrating database to include separate fields for category, ID number, and version...")
                
                # Create a temporary table with the new schema
                cursor.execute('''
                    CREATE TABLE papers_new (
                        paper_id TEXT PRIMARY KEY,
                        category TEXT,
                        id_number TEXT NOT NULL,
                        version TEXT,
                        title TEXT,
                        authors TEXT,
                        downloaded_at TIMESTAMP,
                        directory TEXT NOT NULL,
                        has_metadata BOOLEAN DEFAULT 0,
                        has_pdf BOOLEAN DEFAULT 0
                    )
                ''')
                
                # Copy data from old table to new table, extracting the parts of the paper_id
                cursor.execute("SELECT * FROM papers")
                papers = cursor.fetchall()
                
                for paper in papers:
                    paper_id = paper[0]
                    parts = extract_paper_id_parts(paper_id)
                    
                    cursor.execute('''
                        INSERT INTO papers_new 
                        (paper_id, category, id_number, version, title, authors, downloaded_at, directory, has_metadata, has_pdf)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        paper_id, 
                        parts['category'], 
                        parts['id_number'], 
                        parts['version'], 
                        paper[2],  # title
                        paper[3],  # authors
                        paper[4],  # downloaded_at
                        paper[5],  # directory
                        paper[6],  # has_metadata
                        paper[7]   # has_pdf
                    ))
                
                # Drop the old table and rename the new one
                cursor.execute("DROP TABLE papers")
                cursor.execute("ALTER TABLE papers_new RENAME TO papers")
        else:
            # Create the papers table with the new schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    category TEXT,
                    id_number TEXT NOT NULL,
                    version TEXT,
                    title TEXT,
                    authors TEXT,
                    downloaded_at TIMESTAMP,
                    directory TEXT NOT NULL,
                    has_metadata BOOLEAN DEFAULT 0,
                    has_pdf BOOLEAN DEFAULT 0
                )
            ''')
        
        # Create indexes for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_id_number ON papers (id_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON papers (category)')
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        conn.close()


def record_paper_download(
    paper_id: str, 
    title: str = "", 
    authors: str = "", 
    directory: str = "", 
    has_metadata: bool = False, 
    has_pdf: bool = False,
    category: Optional[str] = None
) -> bool:
    """
    Record a paper download in the SQLite database.
    
    Parameters:
        paper_id (str): The full arXiv ID
        title (str): The paper title
        authors (str): The authors (comma-separated)
        directory (str): The directory where the paper files are stored
        has_metadata (bool): Whether metadata files were extracted
        has_pdf (bool): Whether the PDF was downloaded
        category (str, optional): The paper category (overrides parts['category'] if provided)
        
    Returns:
        bool: True if the record was successfully inserted or updated
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Extract paper ID parts
        parts = extract_paper_id_parts(paper_id)
        
        # If category is provided, use it instead of the one from parts
        if category is not None:
            parts['category'] = category
        
        # Check if the paper already exists in the database
        cursor.execute('SELECT paper_id FROM papers WHERE paper_id = ?', (paper_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update the existing record
            cursor.execute('''
                UPDATE papers 
                SET title = ?, authors = ?, downloaded_at = ?, directory = ?,
                    has_metadata = ?, has_pdf = ?, category = ?
                WHERE paper_id = ?
            ''', (title, authors, datetime.now(), directory, has_metadata, has_pdf, parts['category'], paper_id))
        else:
            # Insert a new record
            cursor.execute('''
                INSERT INTO papers 
                (paper_id, category, id_number, version, title, authors, downloaded_at, directory, has_metadata, has_pdf)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper_id, 
                parts['category'], 
                parts['id_number'], 
                parts['version'], 
                title, 
                authors, 
                datetime.now(), 
                directory, 
                has_metadata, 
                has_pdf
            ))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


def update_paper_status(paper_id: str, has_metadata: Optional[bool] = None, has_pdf: Optional[bool] = None) -> bool:
    """
    Update the status of a paper's metadata and PDF in the database.
    
    Parameters:
        paper_id (str): The full arXiv ID
        has_metadata (bool, optional): Set to True if metadata was successfully extracted
        has_pdf (bool, optional): Set to True if PDF was successfully downloaded
        
    Returns:
        bool: True if the record was successfully updated
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Build the SQL update statement based on provided parameters
        sql = 'UPDATE papers SET '
        params = []
        
        if has_metadata is not None:
            sql += 'has_metadata = ?, '
            params.append(has_metadata)
        
        if has_pdf is not None:
            sql += 'has_pdf = ?, '
            params.append(has_pdf)
        
        # Remove trailing comma and space
        sql = sql.rstrip(', ')
        
        # Add the WHERE clause and execute only if there are updates to make
        if params:
            sql += ' WHERE paper_id = ?'
            params.append(paper_id)
            cursor.execute(sql, params)
            conn.commit()
            return True
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


def paper_exists(paper_id: str) -> bool:
    """
    Check if a paper has already been downloaded by querying the database.
    
    Parameters:
        paper_id (str): The paper ID to check
        
    Returns:
        bool: True if the paper exists in the database
    """
    # Initialize the database if it doesn't exist
    if not os.path.exists(DB_FILE):
        initialize_db()
    
    # Check if paper exists in the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT directory, has_metadata, has_pdf FROM papers 
            WHERE paper_id = ?
        ''', (paper_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return False
        
        directory, has_metadata, has_pdf = result
        
        # Verify metadata and PDF files on disk if needed
        if has_metadata and has_pdf:
            # Get the simplified paper ID
            simple_id = get_simplified_paper_id(paper_id)
            safe_paper_id = sanitize_filename(simple_id)
            
            # Verify metadata directory exists and has files
            metadata_dir = os.path.join(safe_paper_id, 'metadata')
            metadata_exists = os.path.exists(metadata_dir) and os.listdir(metadata_dir)
            
            # Verify PDF file exists
            pdf_dir = os.path.join(safe_paper_id, 'pdf')
            pdf_exists = os.path.exists(os.path.join(pdf_dir, f"{simple_id}.pdf"))
            
            # Update database if filesystem state doesn't match database
            if not metadata_exists or not pdf_exists:
                update_paper_status(paper_id, has_metadata=metadata_exists, has_pdf=pdf_exists)
                return metadata_exists and pdf_exists
        
        return has_metadata and has_pdf
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


def search_local_papers(search_term: Optional[str] = None, search_field: Optional[str] = None, limit: int = 100) -> List[Tuple]:
    """
    Search for papers in the local database based on various criteria.
    
    Parameters:
        search_term (str, optional): The term to search for
        search_field (str, optional): The field to search in ('title', 'authors', 'category', 'id')
        limit (int, optional): Maximum number of results to display
        
    Returns:
        list: List of matching paper records
    """
    # Initialize the database if it doesn't exist
    if not os.path.exists(DB_FILE):
        initialize_db()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if the table has the updated schema
        cursor.execute("PRAGMA table_info(papers)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        has_new_schema = 'category' in column_names and 'id_number' in column_names and 'version' in column_names
        
        if not has_new_schema:
            print("This function requires the updated database schema.")
            return []
        
        # Build the query based on the search parameters
        query = '''
            SELECT paper_id, category, id_number, version, title, authors, downloaded_at, directory, has_metadata, has_pdf
            FROM papers
            WHERE 1=1
        '''
        params = []
        
        if search_term and search_field:
            search_term = f"%{search_term}%"  # For partial matching with LIKE
            
            if search_field == 'title':
                query += ' AND title LIKE ?'
                params.append(search_term)
            elif search_field == 'authors':
                query += ' AND authors LIKE ?'
                params.append(search_term)
            elif search_field == 'category':
                query += ' AND category LIKE ?'
                params.append(search_term)
            elif search_field == 'id':
                query += ' AND (paper_id LIKE ? OR id_number LIKE ?)'
                params.extend([search_term, search_term])
        
        query += ' ORDER BY downloaded_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        papers = cursor.fetchall()
        
        if not papers:
            print("No matching papers found.")
            return []
        
        return papers
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()


def list_downloaded_papers() -> List[Tuple]:
    """
    List all papers that have been downloaded and stored in the database.
    
    Returns:
        list: List of paper records
    """
    # Initialize the database if it doesn't exist
    if not os.path.exists(DB_FILE):
        initialize_db()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if the table has the updated schema
        cursor.execute("PRAGMA table_info(papers)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        has_new_schema = 'category' in column_names and 'id_number' in column_names and 'version' in column_names
        
        if has_new_schema:
            cursor.execute('''
                SELECT paper_id, category, id_number, version, title, authors, downloaded_at, directory, has_metadata, has_pdf
                FROM papers
                ORDER BY downloaded_at DESC
            ''')
        else:
            cursor.execute('''
                SELECT paper_id, simple_id, title, authors, downloaded_at, directory, has_metadata, has_pdf
                FROM papers
                ORDER BY downloaded_at DESC
            ''')
        
        papers = cursor.fetchall()
        
        if not papers:
            print("No papers have been downloaded yet.")
            return []
        
        return papers
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()


def get_paper_details(paper_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a paper from the database.
    
    Parameters:
        paper_id (str): The paper ID to retrieve
        
    Returns:
        dict: Dictionary containing paper details or None if not found
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT paper_id, category, id_number, version, title, authors, downloaded_at, directory, has_metadata, has_pdf
            FROM papers
            WHERE paper_id = ?
        ''', (paper_id,))
        
        paper = cursor.fetchone()
        
        if not paper:
            return None
        
        return {
            'paper_id': paper[0],
            'category': paper[1],
            'id_number': paper[2],
            'version': paper[3],
            'title': paper[4],
            'authors': paper[5],
            'downloaded_at': paper[6],
            'directory': paper[7],
            'has_metadata': paper[8],
            'has_pdf': paper[9]
        }
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()


def delete_paper(paper_id: str) -> bool:
    """
    Delete a paper record from the database.
    
    Parameters:
        paper_id (str): The paper ID to delete
        
    Returns:
        bool: True if the record was successfully deleted
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM papers WHERE paper_id = ?', (paper_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()