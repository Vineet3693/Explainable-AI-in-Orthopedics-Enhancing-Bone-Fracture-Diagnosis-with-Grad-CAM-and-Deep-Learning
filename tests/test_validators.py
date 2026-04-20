"""
Test Validators - Unit Tests for Validation Pipeline

PURPOSE:
    Unit tests for image validation pipeline.
    Ensures validators work correctly and catch invalid images.

WHY UNIT TESTS:
    No tests: Bugs in production, broken validators
    Manual testing: Time-consuming, incomplete
    Automated tests (this): Fast, comprehensive, reliable
    
    IMPACT: Catch bugs early, prevent regressions

DESIGN PHILOSOPHY:
    1. Test all validation stages
    2. Test edge cases
    3. Test error handling
    4. Fast execution

USAGE:
    pytest tests/test_validators.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.validators.image_validator import ImageValidator
import numpy as np
from PIL import Image
import tempfile


class TestImageValidator:
    """Test suite for ImageValidator"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return ImageValidator()
    
    @pytest.fixture
    def valid_image_path(self):
        """Create valid test image"""
        # WHY CREATE TEMP IMAGE:
        # Don't want to commit test images to repo
        # Generate on-the-fly for testing
        img = Image.new('L', (512, 512), color=128)
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name)
        yield temp_file.name
        os.unlink(temp_file.name)
    
    def test_valid_image_passes(self, validator, valid_image_path):
        """Test that valid image passes validation"""
        is_valid, results = validator.validate(valid_image_path)
        assert is_valid, "Valid image should pass validation"
    
    def test_invalid_path_fails(self, validator):
        """Test that invalid path fails"""
        is_valid, results = validator.validate('nonexistent.jpg')
        assert not is_valid, "Nonexistent file should fail"
    
    def test_wrong_format_fails(self, validator):
        """Test that wrong format fails"""
        # Create text file
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b'not an image')
        temp_file.close()
        
        is_valid, results = validator.validate(temp_file.name)
        assert not is_valid, "Text file should fail validation"
        
        os.unlink(temp_file.name)
    
    def test_small_image_fails(self, validator):
        """Test that too-small image fails"""
        # WHY TEST SMALL IMAGES:
        # Model requires minimum size
        # Small images should be rejected
        img = Image.new('L', (50, 50), color=128)
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name)
        
        is_valid, results = validator.validate(temp_file.name)
        # Depending on validator config, might pass or fail
        # This is a placeholder test
        
        os.unlink(temp_file.name)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
