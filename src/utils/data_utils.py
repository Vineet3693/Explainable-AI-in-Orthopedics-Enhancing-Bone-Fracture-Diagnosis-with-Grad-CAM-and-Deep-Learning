"""
Data Utilities for Dataset Management

PURPOSE:
    Utilities for loading, splitting, and managing training/validation datasets.
    Essential for model training and evaluation workflows.

WHY DATA UTILITIES:
    Manual data handling: Error-prone, inconsistent splits
    Automated utilities (this): Reproducible, stratified splits, validation
    
    IMPACT: Better model training, reproducible experiments

DESIGN PHILOSOPHY:
    1. Reproducible splits (seeded random state)
    2. Stratified sampling (balanced classes)
    3. Data validation (check for corrupted files)
    4. Flexible formats (support multiple input types)

PROS:
    ✅ Reproducible experiments (same seed = same split)
    ✅ Balanced datasets (stratification)
    ✅ Data validation (catch issues early)
    ✅ Flexible input formats

CONS:
    ❌ Memory intensive for large datasets
    ❌ Requires all data accessible at once
    ❌ Not suitable for streaming data

ALTERNATIVES:
    1. Manual splitting: More control but error-prone
    2. sklearn.model_selection: Good but less customized
    3. PyTorch DataLoader: Better for training but different purpose
    
COMPARISON:
    | Approach          | Reproducible | Stratified | Validation | Flexibility |
    |-------------------|--------------|------------|------------|-------------|
    | Manual            | ❌           | ❌         | ❌         | ✅          |
    | sklearn           | ✅           | ✅         | ❌         | ⚠️          |
    | This utility      | ✅           | ✅         | ✅         | ✅          |
    | PyTorch DataLoader| ✅           | ⚠️         | ❌         | ✅          |

USAGE:
    from src.utils.data_utils import split_dataset, validate_dataset
    
    train, val, test = split_dataset(
        data_dir='data/xrays',
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        stratify=True,
        random_state=42
    )
"""

import os
import random
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging
from collections import Counter

logger = logging.getLogger(__name__)


def split_dataset(
    data_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    stratify: bool = True,
    random_state: int = 42
) -> Tuple[List[str], List[str], List[str]]:
    """
    Split dataset into train/val/test sets
    
    WHY STRATIFIED SPLIT:
        Ensures each split has same class distribution
        Prevents class imbalance in validation/test sets
        More reliable evaluation metrics
    
    WHY RANDOM STATE:
        Reproducibility - same seed gives same split
        Critical for comparing different models
        Enables collaborative research
    
    Args:
        data_dir: Directory containing images
        train_ratio: Proportion for training (0.0-1.0)
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        stratify: Whether to maintain class distribution
        random_state: Seed for reproducibility
        
    Returns:
        Tuple of (train_files, val_files, test_files)
    """
    # WHY VALIDATE RATIOS:
    # Prevent silent errors from incorrect configuration
    # Fail fast with clear error message
    if not abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6:
        raise ValueError(f"Ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}")
    
    # Set random seed for reproducibility
    # WHY SET SEED:
    # Ensures same split every time with same seed
    # Critical for experiment reproducibility
    random.seed(random_state)
    
    # Collect all image files
    data_path = Path(data_dir)
    image_extensions = {'.jpg', '.jpeg', '.png', '.dcm'}
    
    # WHY USE SET FOR EXTENSIONS:
    # O(1) lookup instead of O(n) for list
    # More efficient for checking membership
    all_files = [
        str(f) for f in data_path.rglob('*') 
        if f.suffix.lower() in image_extensions
    ]
    
    if not all_files:
        raise ValueError(f"No images found in {data_dir}")
    
    logger.info(f"Found {len(all_files)} images in {data_dir}")
    
    if stratify:
        # WHY STRATIFY:
        # Maintains class balance across splits
        # More reliable evaluation
        # Prevents lucky/unlucky splits
        
        # Group files by class (assuming directory structure: data_dir/class/image.jpg)
        class_to_files: Dict[str, List[str]] = {}
        for file_path in all_files:
            # Extract class from parent directory name
            class_name = Path(file_path).parent.name
            if class_name not in class_to_files:
                class_to_files[class_name] = []
            class_to_files[class_name].append(file_path)
        
        logger.info(f"Found {len(class_to_files)} classes: {list(class_to_files.keys())}")
        
        # Split each class separately
        train_files, val_files, test_files = [], [], []
        
        for class_name, files in class_to_files.items():
            random.shuffle(files)
            
            n_train = int(len(files) * train_ratio)
            n_val = int(len(files) * val_ratio)
            
            train_files.extend(files[:n_train])
            val_files.extend(files[n_train:n_train + n_val])
            test_files.extend(files[n_train + n_val:])
            
            logger.info(f"Class '{class_name}': {len(files)} total -> "
                       f"{n_train} train, {n_val} val, {len(files) - n_train - n_val} test")
    else:
        # WHY NON-STRATIFIED OPTION:
        # Sometimes you want random split (e.g., regression tasks)
        # Simpler and faster for balanced datasets
        random.shuffle(all_files)
        
        n_train = int(len(all_files) * train_ratio)
        n_val = int(len(all_files) * val_ratio)
        
        train_files = all_files[:n_train]
        val_files = all_files[n_train:n_train + n_val]
        test_files = all_files[n_train + n_val:]
    
    logger.info(f"Split complete: {len(train_files)} train, {len(val_files)} val, {len(test_files)} test")
    
    return train_files, val_files, test_files


def validate_dataset(file_paths: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate dataset files
    
    WHY VALIDATE:
        Corrupted images cause training crashes
        Better to catch issues before training starts
        Saves hours of debugging
    
    Args:
        file_paths: List of file paths to validate
        
    Returns:
        Tuple of (valid_files, invalid_files)
    """
    import cv2
    
    valid_files = []
    invalid_files = []
    
    logger.info(f"Validating {len(file_paths)} files...")
    
    for file_path in file_paths:
        try:
            # WHY TRY TO LOAD:
            # Only way to know if file is corrupted
            # cv2.imread returns None for corrupted files
            img = cv2.imread(file_path)
            
            if img is None:
                invalid_files.append(file_path)
                logger.warning(f"Invalid image: {file_path}")
            else:
                valid_files.append(file_path)
        except Exception as e:
            invalid_files.append(file_path)
            logger.error(f"Error loading {file_path}: {e}")
    
    logger.info(f"Validation complete: {len(valid_files)} valid, {len(invalid_files)} invalid")
    
    return valid_files, invalid_files


def get_class_distribution(file_paths: List[str]) -> Dict[str, int]:
    """
    Get class distribution from file paths
    
    WHY CHECK DISTRIBUTION:
        Detect class imbalance
        Inform sampling strategy
        Validate stratification worked
    
    Args:
        file_paths: List of file paths
        
    Returns:
        Dictionary mapping class name to count
    """
    classes = [Path(f).parent.name for f in file_paths]
    distribution = dict(Counter(classes))
    
    logger.info("Class distribution:")
    for class_name, count in sorted(distribution.items()):
        percentage = (count / len(file_paths)) * 100
        logger.info(f"  {class_name}: {count} ({percentage:.1f}%)")
    
    return distribution


__all__ = [
    'split_dataset',
    'validate_dataset',
    'get_class_distribution'
]
