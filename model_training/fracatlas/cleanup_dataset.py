"""
Dataset Cleanup Script - Find and Remove Corrupted Images

PURPOSE:
    Scan FracAtlas dataset and identify corrupted/incompatible images
    that cause DecodeImage errors during training.

WHAT IT DOES:
    1. Scans all images in Fractured/ and Non_fractured/ folders
    2. Attempts to load each image with PIL and TensorFlow
    3. Identifies images that fail to load
    4. Moves corrupted images to quarantine folder
    5. Reports statistics

USAGE:
    python model_training/fracatlas/cleanup_dataset.py
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import tensorflow as tf
from tqdm import tqdm

def check_image_pil(image_path):
    """Check if image can be loaded with PIL"""
    try:
        img = Image.open(image_path)
        img.verify()  # Verify it's a valid image
        img = Image.open(image_path)  # Reopen after verify
        img.load()  # Actually load the image data
        return True, None
    except Exception as e:
        return False, str(e)

def check_image_tf(image_path):
    """Check if image can be loaded with TensorFlow"""
    try:
        img_raw = tf.io.read_file(image_path)
        img = tf.image.decode_image(img_raw, channels=3)
        img = tf.image.resize(img, [224, 224])
        return True, None
    except Exception as e:
        return False, str(e)

def scan_dataset(data_dir, quarantine_dir):
    """
    Scan dataset and move corrupted images
    
    Args:
        data_dir: Path to FracAtlas/images directory
        quarantine_dir: Path to move corrupted images
    """
    print("=" * 80)
    print("FRACATLAS DATASET CLEANUP")
    print("=" * 80)
    
    # Create quarantine directory
    os.makedirs(quarantine_dir, exist_ok=True)
    os.makedirs(os.path.join(quarantine_dir, 'Fractured'), exist_ok=True)
    os.makedirs(os.path.join(quarantine_dir, 'Non_fractured'), exist_ok=True)
    
    # Statistics
    stats = {
        'total': 0,
        'valid': 0,
        'corrupted': 0,
        'pil_errors': 0,
        'tf_errors': 0,
        'corrupted_files': []
    }
    
    # Scan both folders
    for folder in ['Fractured', 'Non_fractured']:
        folder_path = os.path.join(data_dir, folder)
        
        if not os.path.exists(folder_path):
            print(f"\nWARNING: Folder not found: {folder_path}")
            continue
        
        print(f"\nScanning {folder}...")
        
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            image_files.extend(Path(folder_path).glob(ext))
        
        print(f"Found {len(image_files)} images")
        
        # Check each image
        for img_path in tqdm(image_files, desc=f"Checking {folder}"):
            stats['total'] += 1
            
            # Check with PIL
            pil_ok, pil_error = check_image_pil(str(img_path))
            
            # Check with TensorFlow
            tf_ok, tf_error = check_image_tf(str(img_path))
            
            if not pil_ok or not tf_ok:
                # Image is corrupted
                stats['corrupted'] += 1
                if not pil_ok:
                    stats['pil_errors'] += 1
                if not tf_ok:
                    stats['tf_errors'] += 1
                
                # Move to quarantine
                dest_path = os.path.join(
                    quarantine_dir,
                    folder,
                    img_path.name
                )
                
                try:
                    shutil.move(str(img_path), dest_path)
                    stats['corrupted_files'].append({
                        'file': str(img_path),
                        'folder': folder,
                        'pil_error': pil_error if not pil_ok else None,
                        'tf_error': tf_error if not tf_ok else None
                    })
                    print(f"\nMoved corrupted image: {img_path.name}")
                    if pil_error:
                        print(f"  PIL Error: {pil_error}")
                    if tf_error:
                        print(f"  TF Error: {tf_error}")
                except Exception as e:
                    print(f"\nERROR moving {img_path.name}: {e}")
            else:
                stats['valid'] += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("CLEANUP SUMMARY")
    print("=" * 80)
    print(f"\nTotal images scanned: {stats['total']}")
    print(f"Valid images: {stats['valid']}")
    print(f"Corrupted images: {stats['corrupted']}")
    print(f"  - PIL errors: {stats['pil_errors']}")
    print(f"  - TensorFlow errors: {stats['tf_errors']}")
    
    if stats['corrupted'] > 0:
        print(f"\nCorrupted images moved to: {quarantine_dir}")
        print("\nCorrupted files:")
        for item in stats['corrupted_files']:
            print(f"  - {item['file']}")
    else:
        print("\nNo corrupted images found!")
    
    # Save report
    report_path = os.path.join(quarantine_dir, 'cleanup_report.txt')
    with open(report_path, 'w') as f:
        f.write("FRACATLAS DATASET CLEANUP REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total images scanned: {stats['total']}\n")
        f.write(f"Valid images: {stats['valid']}\n")
        f.write(f"Corrupted images: {stats['corrupted']}\n")
        f.write(f"  - PIL errors: {stats['pil_errors']}\n")
        f.write(f"  - TensorFlow errors: {stats['tf_errors']}\n\n")
        
        if stats['corrupted'] > 0:
            f.write("Corrupted Files:\n")
            f.write("-" * 80 + "\n")
            for item in stats['corrupted_files']:
                f.write(f"\nFile: {item['file']}\n")
                f.write(f"Folder: {item['folder']}\n")
                if item['pil_error']:
                    f.write(f"PIL Error: {item['pil_error']}\n")
                if item['tf_error']:
                    f.write(f"TF Error: {item['tf_error']}\n")
    
    print(f"\nReport saved to: {report_path}")
    
    return stats

def main():
    # Paths
    data_dir = 'data/raw/FracAtlas/images'
    quarantine_dir = 'data/raw/FracAtlas/quarantine'
    
    # Check if dataset exists
    if not os.path.exists(data_dir):
        print(f"ERROR: Dataset not found at {data_dir}")
        return
    
    # Run cleanup
    stats = scan_dataset(data_dir, quarantine_dir)
    
    # Final message
    print("\n" + "=" * 80)
    if stats['corrupted'] == 0:
        print("Dataset is clean! Ready for training.")
    else:
        print(f"Cleanup complete! Removed {stats['corrupted']} corrupted images.")
        print("Dataset is now ready for training.")
    print("=" * 80)

if __name__ == "__main__":
    main()
