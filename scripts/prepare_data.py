"""
Data preparation and preprocessing script

PURPOSE:
    Organizes raw datasets into train/validation/test splits with proper
    directory structure. Handles data cleaning, format conversion, and
    quality filtering before training.

WHY NEEDED:
    - Raw datasets are often unorganized
    - Need consistent train/val/test splits for reproducibility
    - Quality filtering prevents bad data from affecting training
    - Proper organization enables efficient data loading

PROS:
    ✅ Automated data organization
    ✅ Reproducible splits (same seed = same split)
    ✅ Quality filtering built-in
    ✅ Progress tracking
    ✅ Handles multiple dataset formats

CONS:
    ❌ Requires disk space for copies
    ❌ Time-consuming for large datasets
    ❌ May need manual review for edge cases

ALTERNATIVES:
    1. Manual organization: Error-prone, not reproducible
    2. Symlinks instead of copies: Saves space but fragile
    3. On-the-fly preprocessing: Slower training
    4. Database storage: More complex setup

HOW IT AFFECTS APPLICATION:
    - Determines data quality for training
    - Affects model performance (garbage in = garbage out)
    - Enables reproducible experiments
    - Critical for proper evaluation
"""

import os
import shutil
from pathlib import Path
import random
from typing import Tuple, List
from tqdm import tqdm
import argparse
import logging
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreparator:
    """
    Prepare and organize datasets for training
    
    DESIGN PATTERN:
        Builder pattern - constructs complex data structure step by step
        
    WHY CLASS-BASED:
        - Maintains state (paths, splits, statistics)
        - Reusable for different datasets
        - Easy to extend with new preparation steps
        
    ALTERNATIVE:
        Functional approach with multiple functions
        TRADE-OFF: Less state management but more parameter passing
    """
    
    def __init__(
        self,
        raw_dir: str = 'data/raw',
        processed_dir: str = 'data/processed',
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        random_seed: int = 42
    ):
        """
        Initialize data preparator
        
        Args:
            raw_dir: Directory containing raw datasets
                WHY: Separates raw data from processed
                IMPACT: Preserves original data
                
            processed_dir: Output directory for organized data
                WHY: Clean separation of concerns
                STRUCTURE: processed/split/class/images
                
            train_ratio: Proportion for training set
                DEFAULT: 0.7 (70%) - standard in ML
                WHY: Enough data for learning patterns
                
            val_ratio: Proportion for validation set
                DEFAULT: 0.15 (15%) - for hyperparameter tuning
                WHY: Separate from test for unbiased evaluation
                
            test_ratio: Proportion for test set
                DEFAULT: 0.15 (15%) - final evaluation
                WHY: Held-out data for true performance measure
                
            random_seed: Seed for reproducibility
                DEFAULT: 42 (common convention)
                WHY: Ensures same splits across runs
                IMPACT: Critical for reproducible research
        
        SPLIT RATIOS:
            70/15/15 is standard but can be adjusted:
            - Small datasets: 60/20/20 (more validation data)
            - Large datasets: 80/10/10 (training data is abundant)
            - Very small: Use k-fold cross-validation instead
        """
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        
        # Validate split ratios
        # WHY: Prevent silent errors from invalid ratios
        # ALTERNATIVE: Auto-normalize ratios
        if not abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001:
            raise ValueError(f"Split ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}")
        
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        
        # Set random seed for reproducibility
        # WHY: Ensures same splits every time
        # IMPACT: Critical for comparing experiments
        random.seed(random_seed)
        np.random.seed(random_seed)
        
        # Statistics tracking
        # WHY: Monitor data preparation process
        self.stats = {
            'total_images': 0,
            'train_images': 0,
            'val_images': 0,
            'test_images': 0,
            'skipped_images': 0,
            'fractured': 0,
            'normal': 0
        }
    
    def prepare_mura_dataset(self):
        """
        Prepare MURA dataset
        
        PURPOSE:
            Converts MURA's structure to our standard format
            
        MURA STRUCTURE:
            MURA-v1.1/
            ├── train/
            │   ├── XR_WRIST/
            │   │   ├── patient00001/
            │   │   │   ├── study1_positive/
            │   │   │   │   ├── image1.png
            
        OUR STRUCTURE:
            processed/
            ├── train/
            │   ├── fracture/
            │   ├── normal/
            
        WHY RESTRUCTURE:
            - Simpler for data loader
            - Binary classification focus
            - Consistent with other datasets
            
        TRADE-OFF:
            Loses body part information
            SOLUTION: Can add metadata file if needed
        """
        logger.info("Preparing MURA dataset...")
        
        mura_dir = self.raw_dir / 'MURA-v1.1'
        
        if not mura_dir.exists():
            logger.warning(f"MURA dataset not found at {mura_dir}")
            return
        
        # Process train and valid splits
        # WHY SEPARATE: MURA provides its own splits
        # DECISION: Respect original splits or create new ones?
        # CHOICE: Create new splits for consistency with other datasets
        for split in ['train', 'valid']:
            split_dir = mura_dir / split
            
            if not split_dir.exists():
                continue
            
            # Collect all images with labels
            # LABEL EXTRACTION: 'positive' in path = fracture
            # WHY: MURA uses 'positive/negative' naming
            images_with_labels = []
            
            for body_part_dir in split_dir.iterdir():
                if not body_part_dir.is_dir():
                    continue
                
                for patient_dir in body_part_dir.iterdir():
                    if not patient_dir.is_dir():
                        continue
                    
                    for study_dir in patient_dir.iterdir():
                        if not study_dir.is_dir():
                            continue
                        
                        # Determine label from directory name
                        # WHY: MURA convention
                        is_fracture = 'positive' in study_dir.name.lower()
                        
                        for img_file in study_dir.glob('*.png'):
                            images_with_labels.append((img_file, is_fracture))
            
            logger.info(f"Found {len(images_with_labels)} images in MURA {split}")
            
            # Add to overall pool for splitting
            # WHY: Combine all images then split
            # ALTERNATIVE: Keep MURA's original splits
            # CHOICE: New splits for consistency
            self._add_to_pool(images_with_labels)
    
    def prepare_fracatlas_dataset(self):
        """
        Prepare FracAtlas dataset
        
        PURPOSE:
            Converts FracAtlas structure to standard format
            
        FRACATLAS STRUCTURE:
            FracAtlas/
            ├── Fractured/
            │   ├── image1.jpg
            ├── Normal/
            │   ├── image2.jpg
            
        ADVANTAGE:
            Already in binary classification format
            
        PROCESS:
            1. Validate images
            2. Add to pool
            3. Split into train/val/test
        """
        logger.info("Preparing FracAtlas dataset...")
        
        fracatlas_dir = self.raw_dir / 'FracAtlas'
        
        if not fracatlas_dir.exists():
            logger.warning(f"FracAtlas dataset not found at {fracatlas_dir}")
            return
        
        images_with_labels = []
        
        # Process fractured images
        # LABEL: True = fractured
        fractured_dir = fracatlas_dir / 'Fractured'
        if fractured_dir.exists():
            for img_file in fractured_dir.glob('*.[jp][pn]g'):  # .jpg or .png
                images_with_labels.append((img_file, True))
        
        # Process normal images
        # LABEL: False = normal
        normal_dir = fracatlas_dir / 'Normal'
        if normal_dir.exists():
            for img_file in normal_dir.glob('*.[jp][pn]g'):
                images_with_labels.append((img_file, False))
        
        logger.info(f"Found {len(images_with_labels)} images in FracAtlas")
        
        self._add_to_pool(images_with_labels)
    
    def _add_to_pool(self, images_with_labels: List[Tuple[Path, bool]]):
        """
        Add images to the pool for splitting
        
        PURPOSE:
            Centralizes all images before splitting
            
        WHY POOL APPROACH:
            - Ensures balanced splits across datasets
            - Allows global shuffling
            - Simplifies split logic
            
        ALTERNATIVE:
            Split each dataset separately
            TRADE-OFF: May lead to imbalanced splits
        """
        if not hasattr(self, '_image_pool'):
            self._image_pool = []
        
        self._image_pool.extend(images_with_labels)
    
    def create_splits(self):
        """
        Create train/validation/test splits
        
        PURPOSE:
            Divides data into three non-overlapping sets
            
        STRATEGY:
            1. Shuffle all images (randomization)
            2. Split by ratios
            3. Ensure class balance in each split
            
        WHY SHUFFLE FIRST:
            - Prevents ordering bias
            - Ensures random distribution
            
        CLASS BALANCE:
            Stratified splitting ensures similar class ratios
            in each split (important for small datasets)
            
        ALTERNATIVE:
            Random split without stratification
            RISK: May get imbalanced splits
        """
        if not hasattr(self, '_image_pool'):
            logger.error("No images in pool. Run prepare_*_dataset() first.")
            return
        
        logger.info(f"Creating splits from {len(self._image_pool)} images...")
        
        # Separate by class for stratified splitting
        # WHY STRATIFY: Ensures balanced class distribution
        # IMPACT: Prevents one split from being all fractures/normals
        fractured_images = [img for img, label in self._image_pool if label]
        normal_images = [img for img, label in self._image_pool if not label]
        
        # Shuffle within each class
        # WHY: Randomize order before splitting
        random.shuffle(fractured_images)
        random.shuffle(normal_images)
        
        # Calculate split indices
        # MATH: Use ratios to determine split points
        n_fractured = len(fractured_images)
        n_normal = len(normal_images)
        
        # Fractured splits
        frac_train_idx = int(n_fractured * self.train_ratio)
        frac_val_idx = int(n_fractured * (self.train_ratio + self.val_ratio))
        
        # Normal splits
        norm_train_idx = int(n_normal * self.train_ratio)
        norm_val_idx = int(n_normal * (self.train_ratio + self.val_ratio))
        
        # Create split dictionaries
        # STRUCTURE: {split: [(path, label), ...]}
        splits = {
            'train': (
                [(p, True) for p in fractured_images[:frac_train_idx]] +
                [(p, False) for p in normal_images[:norm_train_idx]]
            ),
            'validation': (
                [(p, True) for p in fractured_images[frac_train_idx:frac_val_idx]] +
                [(p, False) for p in normal_images[norm_train_idx:norm_val_idx]]
            ),
            'test': (
                [(p, True) for p in fractured_images[frac_val_idx:]] +
                [(p, False) for p in normal_images[norm_val_idx:]]
            )
        }
        
        # Copy files to organized structure
        # WHY COPY: Preserves original data
        # ALTERNATIVE: Symlinks (saves space but fragile)
        for split_name, images in splits.items():
            self._copy_split(split_name, images)
        
        # Print statistics
        self._print_statistics()
    
    def _copy_split(self, split_name: str, images: List[Tuple[Path, bool]]):
        """
        Copy images to split directory
        
        PURPOSE:
            Organizes images into final directory structure
            
        PROCESS:
            1. Create directories
            2. Validate images
            3. Copy with progress bar
            
        ERROR HANDLING:
            Skips corrupted images
            WHY: Prevents training failures
        """
        logger.info(f"Copying {len(images)} images to {split_name} split...")
        
        # Create directories
        # STRUCTURE: processed/split/class/
        fracture_dir = self.processed_dir / split_name / 'fracture'
        normal_dir = self.processed_dir / split_name / 'normal'
        
        fracture_dir.mkdir(parents=True, exist_ok=True)
        normal_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy images with progress bar
        # WHY TQDM: Visual feedback for long operations
        for img_path, is_fracture in tqdm(images, desc=f"Copying {split_name}"):
            try:
                # Validate image can be opened
                # WHY: Catch corrupted images early
                # ALTERNATIVE: Copy blindly (faster but risky)
                with Image.open(img_path) as img:
                    img.verify()  # Check integrity
                
                # Determine destination
                dest_dir = fracture_dir if is_fracture else normal_dir
                dest_path = dest_dir / img_path.name
                
                # Copy file
                # WHY shutil.copy2: Preserves metadata
                # ALTERNATIVE: shutil.copy (faster, no metadata)
                shutil.copy2(img_path, dest_path)
                
                # Update statistics
                self.stats['total_images'] += 1
                self.stats[f'{split_name}_images'] += 1
                if is_fracture:
                    self.stats['fractured'] += 1
                else:
                    self.stats['normal'] += 1
                    
            except Exception as e:
                logger.warning(f"Skipping corrupted image {img_path}: {e}")
                self.stats['skipped_images'] += 1
    
    def _print_statistics(self):
        """
        Print preparation statistics
        
        PURPOSE:
            Provides summary of data preparation
            
        WHY IMPORTANT:
            - Verify splits are correct
            - Detect class imbalance
            - Track data quality issues
        """
        logger.info("\n" + "=" * 60)
        logger.info("Data Preparation Statistics")
        logger.info("=" * 60)
        logger.info(f"Total images processed: {self.stats['total_images']}")
        logger.info(f"Skipped (corrupted): {self.stats['skipped_images']}")
        logger.info(f"\nSplit Distribution:")
        logger.info(f"  Train: {self.stats['train_images']} ({self.stats['train_images']/self.stats['total_images']:.1%})")
        logger.info(f"  Validation: {self.stats['val_images']} ({self.stats['val_images']/self.stats['total_images']:.1%})")
        logger.info(f"  Test: {self.stats['test_images']} ({self.stats['test_images']/self.stats['total_images']:.1%})")
        logger.info(f"\nClass Distribution:")
        logger.info(f"  Fractured: {self.stats['fractured']} ({self.stats['fractured']/self.stats['total_images']:.1%})")
        logger.info(f"  Normal: {self.stats['normal']} ({self.stats['normal']/self.stats['total_images']:.1%})")


def main():
    """
    Main function
    
    PURPOSE:
        Entry point for data preparation
        
    WORKFLOW:
        1. Parse arguments
        2. Initialize preparator
        3. Prepare each dataset
        4. Create splits
        5. Report statistics
    """
    parser = argparse.ArgumentParser(
        description='Prepare datasets for fracture detection training'
    )
    
    parser.add_argument(
        '--raw-dir',
        type=str,
        default='data/raw',
        help='Directory containing raw datasets'
    )
    
    parser.add_argument(
        '--processed-dir',
        type=str,
        default='data/processed',
        help='Output directory for processed data'
    )
    
    parser.add_argument(
        '--train-ratio',
        type=float,
        default=0.7,
        help='Training set ratio (default: 0.7)'
    )
    
    parser.add_argument(
        '--val-ratio',
        type=float,
        default=0.15,
        help='Validation set ratio (default: 0.15)'
    )
    
    parser.add_argument(
        '--test-ratio',
        type=float,
        default=0.15,
        help='Test set ratio (default: 0.15)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    
    args = parser.parse_args()
    
    # Initialize preparator
    preparator = DataPreparator(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        random_seed=args.seed
    )
    
    # Prepare datasets
    preparator.prepare_mura_dataset()
    preparator.prepare_fracatlas_dataset()
    
    # Create splits
    preparator.create_splits()
    
    logger.info("\n✅ Data preparation complete!")
    logger.info(f"Processed data saved to: {args.processed_dir}")
    logger.info("\nNext step: python scripts/train.py")


if __name__ == "__main__":
    main()
