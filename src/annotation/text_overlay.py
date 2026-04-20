"""
Text Overlay for Image Annotation

PURPOSE:
    Adds text annotations, arrows, and labels to X-ray images.
    Useful for highlighting fracture locations and findings.

USAGE:
    from src.annotation.text_overlay import add_text_overlay
    
    annotated_img = add_text_overlay(
        image,
        text='Fracture detected',
        position=(100, 100)
    )
"""

import cv2
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def add_text_overlay(
    image: np.ndarray,
    text: str,
    position: Tuple[int, int],
    font_scale: float = 1.0,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """
    Add text overlay to image
    
    Args:
        image: Input image
        text: Text to add
        position: (x, y) position
        font_scale: Font size scale
        color: Text color (B, G, R)
        thickness: Text thickness
        
    Returns:
        Annotated image
    """
    annotated = image.copy()
    cv2.putText(
        annotated,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness
    )
    return annotated


def add_arrow(
    image: np.ndarray,
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """Add arrow annotation"""
    annotated = image.copy()
    cv2.arrowedLine(annotated, start, end, color, thickness)
    return annotated


__all__ = ['add_text_overlay', 'add_arrow']
