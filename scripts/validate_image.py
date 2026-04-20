"""
Validate Image Script

PURPOSE:
    Standalone script to validate X-ray images using the validation pipeline.

USAGE:
    python scripts/validate_image.py --image path/to/xray.jpg
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.validators.image_validator import ImageValidator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Validate X-ray image')
    parser.add_argument('--image', required=True, help='Path to X-ray image')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate image
    validator = ImageValidator()
    is_valid, results = validator.validate(args.image)
    
    # Print results
    print(f"\nValidation Results for: {args.image}")
    print(f"Valid: {is_valid}")
    print(f"\nDetails:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    return 0 if is_valid else 1


if __name__ == '__main__':
    sys.exit(main())
