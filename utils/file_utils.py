#!/usr/bin/env python3
"""
File utility functions for the arXiv Paper Manager.

This module provides functions for file operations such as:
- Creating directories
- Saving content to files
- File path manipulation
"""

import os
import re
from typing import Optional, Union, List


def sanitize_filename(name: str) -> str:
    """
    Replace characters that are not alphanumeric, dash, underscore, or dot with underscores.
    This helps in creating a safe directory name.
    
    Parameters:
        name (str): The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    return re.sub(r'[^\w\-_\.]', '_', name)


def ensure_dir_exists(directory: str) -> bool:
    """
    Create a directory if it does not already exist.
    
    Parameters:
        directory (str): The directory path to create
        
    Returns:
        bool: True if the directory exists or was created successfully
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False


def save_to_file(content: Union[str, bytes], file_path: str) -> bool:
    """
    Save content to a file, creating parent directories if needed.
    
    Parameters:
        content (str or bytes): The content to write to the file
        file_path (str): The full path to the file
        
    Returns:
        bool: True if the file was written successfully
    """
    try:
        directory = os.path.dirname(file_path)
        ensure_dir_exists(directory)
        
        # Check if content is binary
        if isinstance(content, bytes):
            with open(file_path, 'wb') as file:
                file.write(content)
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False
        

def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """
    List files in a directory, optionally filtering by pattern.
    
    Parameters:
        directory (str): The directory to list files from
        pattern (str, optional): A glob pattern to filter files
        
    Returns:
        list: List of file paths
    """
    import glob
    
    if pattern:
        return glob.glob(os.path.join(directory, pattern))
    else:
        try:
            return [
                os.path.join(directory, f) 
                for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f))
            ]
        except Exception as e:
            print(f"Error listing files in {directory}: {e}")
            return []