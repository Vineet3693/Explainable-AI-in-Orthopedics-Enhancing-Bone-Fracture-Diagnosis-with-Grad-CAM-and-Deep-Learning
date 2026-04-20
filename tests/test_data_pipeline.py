"""
Test suite for data pipeline
"""

import pytest
import numpy as np
from src.data.dataset import FractureDataset
from src.data.preprocessing import ImagePreprocessor
from src.data.augmentation import XRayAugmentor


class TestFractureDataset:
    """Test FractureDataset class"""
    
    def test_dataset_initialization(self):
        """Test dataset initialization"""
        # This would need actual data
        pass
    
    def test_dataset_length(self):
        """Test dataset length calculation"""
        pass
    
    def test_class_distribution(self):
        """Test class distribution calculation"""
        pass


class TestImagePreprocessor:
    """Test ImagePreprocessor class"""
    
    def test_resize(self):
        """Test image resizing"""
        preprocessor = ImagePreprocessor(target_size=(224, 224))
        
        # Create dummy image
        img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        
        # Resize
        resized = preprocessor.resize(img, (224, 224))
        
        assert resized.shape == (224, 224, 3)
    
    def test_normalize(self):
        """Test image normalization"""
        preprocessor = ImagePreprocessor()
        
        img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        # Normalize
        normalized = preprocessor.normalize_image(img, method='standard')
        
        assert normalized.max() <= 1.0
        assert normalized.min() >= 0.0
    
    def test_clahe_enhancement(self):
        """Test CLAHE enhancement"""
        preprocessor = ImagePreprocessor(apply_clahe=True)
        
        img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        # Apply CLAHE
        enhanced = preprocessor.apply_clahe_enhancement(img)
        
        assert enhanced.shape == img.shape


class TestXRayAugmentor:
    """Test XRayAugmentor class"""
    
    def test_augmentor_initialization(self):
        """Test augmentor initialization"""
        augmentor = XRayAugmentor(image_size=(224, 224))
        
        assert augmentor.image_size == (224, 224)
        assert augmentor.train_transform is not None
    
    def test_rotation(self):
        """Test random rotation"""
        img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        rotated = XRayAugmentor.random_rotation(img, max_angle=15)
        
        assert rotated.shape == img.shape
    
    def test_noise_addition(self):
        """Test Gaussian noise addition"""
        img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        noisy = XRayAugmentor.add_gaussian_noise(img, std=25)
        
        assert noisy.shape == img.shape


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
