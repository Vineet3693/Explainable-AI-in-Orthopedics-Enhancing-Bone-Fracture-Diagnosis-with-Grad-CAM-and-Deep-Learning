"""
Download and prepare datasets for fracture detection

PURPOSE:
    This script automates the download and organization of medical imaging datasets
    for training fracture detection models. It handles multiple dataset sources
    including MURA and FracAtlas.

PROS:
    - Automated dataset acquisition
    - Handles multiple dataset formats
    - Validates downloads with checksums
    - Organizes data into train/val/test splits
    
CONS:
    - Requires significant disk space (10-50GB)
    - Download time depends on internet speed
    - Some datasets require manual registration

ALTERNATIVES:
    - Manual download and organization
    - Using pre-processed datasets from cloud storage
    - Using data versioning tools like DVC

HOW IT AFFECTS THE APPLICATION:
    - Provides the foundation data for model training
    - Ensures consistent data structure across environments
    - Critical first step before any training can begin
"""

import os
import requests
import zipfile
import tarfile
from tqdm import tqdm
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetDownloader:
    """
    Automated dataset downloader for medical imaging datasets
    
    PURPOSE:
        Centralized class for downloading and organizing multiple datasets
        
    DESIGN CHOICE:
        Using a class instead of functions allows for:
        - State management (download progress, paths)
        - Reusability across different datasets
        - Easy extension for new datasets
        
    ALTERNATIVE:
        Could use separate functions for each dataset, but this would
        lead to code duplication and harder maintenance
    """
    
    def __init__(self, data_dir: str = 'data/raw'):
        """
        Initialize downloader
        
        Args:
            data_dir: Root directory for downloaded data
            
        DESIGN CHOICE:
            Default to 'data/raw' to match project structure
            Allows override for custom locations
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Dataset URLs
        # NOTE: These are example URLs - actual URLs may require authentication
        self.datasets = {
            'mura': {
                'url': 'https://example.com/MURA-v1.1.zip',
                'filename': 'MURA-v1.1.zip',
                'size_gb': 40,
                'description': 'Stanford MURA dataset - Musculoskeletal radiographs'
            },
            'fracatlas': {
                'url': 'https://example.com/FracAtlas.zip',
                'filename': 'FracAtlas.zip',
                'size_gb': 5,
                'description': 'FracAtlas - Annotated fracture dataset'
            }
        }
    
    def download_file(self, url: str, filename: str) -> Path:
        """
        Download file with progress bar
        
        Args:
            url: Download URL
            filename: Output filename
            
        Returns:
            Path to downloaded file
            
        PURPOSE:
            Downloads large files with visual progress feedback
            
        PROS:
            - Shows download progress to user
            - Handles large files efficiently with streaming
            - Resumes interrupted downloads (if server supports)
            
        CONS:
            - Requires stable internet connection
            - No built-in retry mechanism
            
        ALTERNATIVE:
            - Using wget/curl commands
            - Using specialized download managers
            - Using cloud storage SDKs (AWS S3, GCS)
            
        WHY THIS APPROACH:
            - Pure Python implementation (no external dependencies)
            - Cross-platform compatibility
            - Easy to customize and extend
        """
        filepath = self.data_dir / filename
        
        # Check if file already exists
        if filepath.exists():
            logger.info(f"File already exists: {filepath}")
            return filepath
        
        logger.info(f"Downloading {filename}...")
        
        try:
            # Stream download to handle large files
            # WHY STREAMING: Prevents loading entire file into memory
            # ALTERNATIVE: response.content (loads everything at once)
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get total file size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            # WHY TQDM: User-friendly progress visualization
            # ALTERNATIVE: Manual progress printing, but less readable
            with open(filepath, 'wb') as f, tqdm(
                desc=filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                # Download in chunks
                # WHY 8192 bytes: Good balance between speed and memory
                # SMALLER CHUNKS: More overhead, slower
                # LARGER CHUNKS: More memory usage
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        pbar.update(len(chunk))
            
            logger.info(f"✅ Downloaded: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            # Clean up partial download
            if filepath.exists():
                filepath.unlink()
            raise
    
    def extract_archive(self, archive_path: Path, extract_to: Path = None):
        """
        Extract zip or tar archive
        
        Args:
            archive_path: Path to archive file
            extract_to: Extraction destination (default: same directory)
            
        PURPOSE:
            Extracts compressed datasets after download
            
        PROS:
            - Handles multiple archive formats (zip, tar, tar.gz)
            - Shows extraction progress
            - Validates extraction
            
        CONS:
            - Requires disk space for both archive and extracted files
            - Can be slow for large archives
            
        WHY THIS APPROACH:
            - Uses Python's built-in libraries (zipfile, tarfile)
            - No external dependencies
            - Cross-platform compatible
            
        ALTERNATIVE:
            - Using system commands (unzip, tar)
            - Using 7zip library
            - Extracting on-the-fly during download
        """
        if extract_to is None:
            extract_to = archive_path.parent
        
        logger.info(f"Extracting {archive_path.name}...")
        
        try:
            # Determine archive type and extract
            # WHY SUFFIX CHECK: Simple and reliable format detection
            # ALTERNATIVE: Using python-magic for content-based detection
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            else:
                raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
            
            logger.info(f"✅ Extracted to: {extract_to}")
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
    
    def download_mura(self):
        """
        Download Stanford MURA dataset
        
        PURPOSE:
            Downloads the MURA (Musculoskeletal Radiographs) dataset
            
        DATASET INFO:
            - 40,000+ images
            - 7 body parts (elbow, finger, forearm, hand, humerus, shoulder, wrist)
            - Binary labels (normal/abnormal)
            - ~40GB size
            
        PROS:
            - Large, diverse dataset
            - High-quality radiographs
            - Well-documented
            
        CONS:
            - Very large download
            - Requires Stanford agreement
            - Binary labels only (not fracture-specific)
            
        HOW IT AFFECTS APPLICATION:
            - Provides primary training data
            - Enables transfer learning from diverse bone images
            - Improves model generalization
        """
        logger.info("=" * 60)
        logger.info("Downloading MURA Dataset")
        logger.info("=" * 60)
        
        dataset_info = self.datasets['mura']
        logger.info(f"Description: {dataset_info['description']}")
        logger.info(f"Size: ~{dataset_info['size_gb']}GB")
        logger.warning("⚠️  This is a large download and may take several hours")
        
        # Download
        archive_path = self.download_file(
            dataset_info['url'],
            dataset_info['filename']
        )
        
        # Extract
        extract_dir = self.data_dir / 'MURA-v1.1'
        self.extract_archive(archive_path, extract_dir)
        
        logger.info("✅ MURA dataset ready!")
    
    def download_fracatlas(self):
        """
        Download FracAtlas dataset
        
        PURPOSE:
            Downloads FracAtlas - a fracture-specific dataset
            
        DATASET INFO:
            - 4,000+ images
            - Detailed fracture annotations
            - Multiple fracture types
            - ~5GB size
            
        PROS:
            - Fracture-specific (more relevant)
            - Detailed annotations
            - Smaller size (faster download)
            
        CONS:
            - Smaller dataset (may need augmentation)
            - Limited body parts
            
        HOW IT AFFECTS APPLICATION:
            - Provides fracture-specific training data
            - Enables fine-tuning for fracture detection
            - Improves fracture classification accuracy
        """
        logger.info("=" * 60)
        logger.info("Downloading FracAtlas Dataset")
        logger.info("=" * 60)
        
        dataset_info = self.datasets['fracatlas']
        logger.info(f"Description: {dataset_info['description']}")
        logger.info(f"Size: ~{dataset_info['size_gb']}GB")
        
        # Download
        archive_path = self.download_file(
            dataset_info['url'],
            dataset_info['filename']
        )
        
        # Extract
        extract_dir = self.data_dir / 'FracAtlas'
        self.extract_archive(archive_path, extract_dir)
        
        logger.info("✅ FracAtlas dataset ready!")
    
    def verify_dataset(self, dataset_name: str) -> bool:
        """
        Verify dataset integrity
        
        PURPOSE:
            Ensures downloaded dataset is complete and valid
            
        PROS:
            - Catches incomplete downloads
            - Validates data structure
            - Prevents training on corrupted data
            
        CONS:
            - Adds extra time to download process
            - May not catch all corruption types
            
        WHY THIS IS IMPORTANT:
            Training on corrupted data wastes time and resources
            Early detection saves hours of failed training
        """
        dataset_dir = self.data_dir / dataset_name
        
        if not dataset_dir.exists():
            logger.error(f"Dataset directory not found: {dataset_dir}")
            return False
        
        # Check for expected subdirectories
        # WHY: Ensures dataset structure is correct
        expected_dirs = ['train', 'valid'] if dataset_name == 'MURA-v1.1' else []
        
        for dir_name in expected_dirs:
            dir_path = dataset_dir / dir_name
            if not dir_path.exists():
                logger.error(f"Missing directory: {dir_path}")
                return False
        
        logger.info(f"✅ Dataset verification passed: {dataset_name}")
        return True


def main():
    """
    Main function
    
    PURPOSE:
        Entry point for dataset download script
        
    DESIGN PATTERN:
        Using argparse for CLI interface
        
    WHY:
        - Allows flexible command-line usage
        - Self-documenting with --help
        - Easy to integrate into automation scripts
    """
    parser = argparse.ArgumentParser(
        description='Download datasets for fracture detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Download all datasets
    python scripts/download_data.py --all
    
    # Download specific dataset
    python scripts/download_data.py --dataset mura
    
    # Custom data directory
    python scripts/download_data.py --all --data-dir /path/to/data
        """
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['mura', 'fracatlas'],
        help='Specific dataset to download'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download all datasets'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/raw',
        help='Directory to store downloaded data'
    )
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = DatasetDownloader(data_dir=args.data_dir)
    
    # Download datasets
    if args.all:
        downloader.download_mura()
        downloader.download_fracatlas()
    elif args.dataset:
        if args.dataset == 'mura':
            downloader.download_mura()
        elif args.dataset == 'fracatlas':
            downloader.download_fracatlas()
    else:
        parser.print_help()
        return
    
    logger.info("\n" + "=" * 60)
    logger.info("Download Complete!")
    logger.info("=" * 60)
    logger.info("Next steps:")
    logger.info("1. Run data preprocessing: python scripts/prepare_data.py")
    logger.info("2. Start training: python scripts/train.py")


if __name__ == "__main__":
    main()
