"""
File Utilities

PURPOSE:
    Helper functions for file I/O operations.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def ensure_dir(directory: str):
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)


def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    List all files in directory
    
    Args:
        directory: Directory path
        extension: File extension filter (e.g., '.jpg')
        
    Returns:
        List of file paths
    """
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if extension is None or filename.endswith(extension):
                files.append(os.path.join(root, filename))
    return files


def copy_file(src: str, dst: str):
    """Copy file from src to dst"""
    ensure_dir(os.path.dirname(dst))
    shutil.copy2(src, dst)
    logger.debug(f"Copied {src} -> {dst}")


def move_file(src: str, dst: str):
    """Move file from src to dst"""
    ensure_dir(os.path.dirname(dst))
    shutil.move(src, dst)
    logger.debug(f"Moved {src} -> {dst}")


def delete_file(path: str):
    """Delete file"""
    if os.path.exists(path):
        os.remove(path)
        logger.debug(f"Deleted {path}")


def read_json(path: str) -> dict:
    """Read JSON file"""
    with open(path, 'r') as f:
        return json.load(f)


def write_json(data: dict, path: str, indent: int = 2):
    """Write JSON file"""
    ensure_dir(os.path.dirname(path))
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)


def get_file_size(path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(path)


def get_file_extension(path: str) -> str:
    """Get file extension"""
    return os.path.splitext(path)[1]


__all__ = [
    'ensure_dir',
    'list_files',
    'copy_file',
    'move_file',
    'delete_file',
    'read_json',
    'write_json',
    'get_file_size',
    'get_file_extension'
]
