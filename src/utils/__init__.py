"""
Utilities package for helper functions

PACKAGE PURPOSE:
    Contains utility functions and helper classes used across the project.

POTENTIAL UTILITIES:
    - image_utils.py: Image manipulation helpers
    - file_utils.py: File I/O helpers
    - config_utils.py: Configuration loading
    - metrics_utils.py: Metric calculation helpers
    - visualization_utils.py: Plotting and visualization

KEY CONCEPTS:
    - DRY: Don't Repeat Yourself (reusable functions)
    - Single Responsibility: Each utility does one thing well
    - Pure Functions: No side effects, same input = same output
    - Type Hints: Clear function signatures

USAGE:
    from src.utils import load_config, save_image
    
    config = load_config('config.yaml')
    save_image(image_array, 'output.jpg')
"""

import os
import yaml
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def save_json(data: Dict, filepath: str):
    """
    Save dictionary to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Output file path
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(filepath: str) -> Dict:
    """
    Load JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded dictionary
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


__all__ = [
    'load_config',
    'save_json',
    'load_json'
]
