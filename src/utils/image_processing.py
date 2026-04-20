"""
Image Processing Utilities

PURPOSE:
    Helper functions for common image operations (resize, normalize, convert).
    Ensures consistent image input for models.

USAGE:
    from src.utils.image_processing import process_image_for_model
"""

import cv2
import numpy as np
from typing import Tuple, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_image(image_source: Union[str, Path, bytes]) -> np.ndarray:
    """
    Load image from various sources
    
    Args:
        image_source: Path or bytes
        
    Returns:
        Numpy array (BGR)
    """
    try:
        if isinstance(image_source, (str, Path)):
            img = cv2.imread(str(image_source))
            if img is None:
                raise ValueError(f"Could not read image from {image_source}")
            return img
        elif isinstance(image_source, bytes):
            nparr = np.frombuffer(image_source, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image bytes")
            return img
        else:
            raise TypeError(f"Unsupported image source type: {type(image_source)}")
    except Exception as e:
        logger.error(f"Image load error: {e}")
        raise

def preprocess_for_model(
    image: np.ndarray,
    target_size: Tuple[int, int] = (224, 224),
    normalize: bool = True
) -> np.ndarray:
    """
    Preprocess image for CNN inference
    
    Args:
        image: Input image
        target_size: (width, height)
        normalize: Whether to normalize pixel values to [0,1]
    
    Returns:
        Preprocessed image batch (1, C, H, W) or (1, H, W, C)
    """
    # Resize
    img = cv2.resize(image, target_size)
    
    # Convert to RGB (OpenCV is BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Normalize
    img = img.astype(np.float32)
    if normalize:
        img /= 255.0
        
    # Add batch dimension
    # Most frameworks expect (Batch, Height, Width, Channels) or (Batch, Channels, Height, Width)
    # Returning (1, H, W, C) for general usage
    img_batch = np.expand_dims(img, axis=0)
    
    return img_batch

def enhance_contrast(image: np.ndarray) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
    # Convert to LAB
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L-channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    
    # Merge and convert back
    limg = cv2.merge((cl, a, b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    return final

__all__ = ['load_image', 'preprocess_for_model', 'enhance_contrast']
