"""
Comparison Generator for Image Comparison

PURPOSE:
    Generates side-by-side comparisons of X-ray images.
    Used for monitoring healing progress or comparing with normal examples.

WHY COMPARISON GENERATOR:
    Visual comparison is crucial for tracking healing.
    Automated alignment and visualization helps radiologists.

USAGE:
    from src.annotation.comparison_generator import ComparisonGenerator

    generator = ComparisonGenerator()
    comparison_img = generator.create_comparison(
        img1=current_xray,
        img2=previous_xray,
        label1="Current",
        label2="Previous"
    )
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ComparisonGenerator:
    """Generates visual comparisons of images"""

    def __init__(self):
        pass

    def create_comparison(
        self,
        img1: np.ndarray,
        img2: np.ndarray,
        label1: str = "Image 1",
        label2: str = "Image 2",
        resize_to_match: bool = True
    ) -> np.ndarray:
        """
        Create side-by-side comparison

        Args:
            img1: First image (numpy array)
            img2: Second image (numpy array)
            label1: Label for first image
            label2: Label for second image
            resize_to_match: Whether to resize images to match height

        Returns:
            Concatenated image with labels
        """
        if img1 is None or img2 is None:
            raise ValueError("Input images cannot be None")

        # Ensure images are in BGR format for text overlay
        if len(img1.shape) == 2:
            img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
        if len(img2.shape) == 2:
            img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

        # Resize to match height if requested
        if resize_to_match and img1.shape[0] != img2.shape[0]:
            h1, w1 = img1.shape[:2]
            h2, w2 = img2.shape[:2]
            
            # Resize second image to match first image's height
            new_w2 = int(w2 * (h1 / h2))
            img2 = cv2.resize(img2, (new_w2, h1))

        # Add labels
        img1_labeled = self._add_label(img1, label1)
        img2_labeled = self._add_label(img2, label2)

        # Concatenate horizontally
        # WHY HORIZONTAL:
        # Standard medical layout for comparison (current vs previous)
        comparison = np.hstack((img1_labeled, img2_labeled))

        return comparison

    def _add_label(
        self,
        image: np.ndarray,
        text: str,
        color: Tuple[int, int, int] = (255, 255, 255),
        bg_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> np.ndarray:
        """Add text label to image top-left"""
        labeled = image.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1.0
        thickness = 2
        margin = 10

        # Get text size
        (text_w, text_h), baseline = cv2.getTextSize(text, font, scale, thickness)

        # Draw background rectangle
        cv2.rectangle(
            labeled,
            (0, 0),
            (text_w + 2 * margin, text_h + 2 * margin),
            bg_color,
            -1
        )

        # Draw text
        cv2.putText(
            labeled,
            text,
            (margin, text_h + margin),
            font,
            scale,
            color,
            thickness
        )

        return labeled


__all__ = ['ComparisonGenerator']
