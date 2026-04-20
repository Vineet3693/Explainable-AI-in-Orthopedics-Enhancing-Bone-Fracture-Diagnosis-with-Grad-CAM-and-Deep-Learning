"""
Grad-CAM Overlay for Explainability

PURPOSE:
    Overlays Grad-CAM heatmaps on X-ray images to show where
    the model is looking when making predictions.

USAGE:
    from src.annotation.gradcam_overlay import overlay_gradcam
    
    annotated = overlay_gradcam(image, heatmap, alpha=0.4)
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


def overlay_gradcam(
    image: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.4,
    colormap: int = cv2.COLORMAP_JET
) -> np.ndarray:
    """
    Overlay Grad-CAM heatmap on image
    
    Args:
        image: Original X-ray image
        heatmap: Grad-CAM heatmap
        alpha: Transparency (0-1)
        colormap: OpenCV colormap
        
    Returns:
        Image with heatmap overlay
    """
    # Resize heatmap to match image
    heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
    
    # Normalize heatmap
    heatmap = np.uint8(255 * heatmap)
    
    # Apply colormap
    heatmap_colored = cv2.applyColorMap(heatmap, colormap)
    
    # Overlay
    overlayed = cv2.addWeighted(image, 1 - alpha, heatmap_colored, alpha, 0)
    
    return overlayed


__all__ = ['overlay_gradcam']
