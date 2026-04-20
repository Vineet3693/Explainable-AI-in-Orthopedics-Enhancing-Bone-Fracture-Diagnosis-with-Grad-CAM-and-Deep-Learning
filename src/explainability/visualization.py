"""
Visualization Utilities for Explainability

PURPOSE:
    Provides visualization functions for model explanations.
    Creates publication-quality figures for reports and presentations.

WHY VISUALIZATION UTILITIES:
    Raw explanations: Hard to interpret
    Visualizations (this): Clear, professional, actionable
    
    IMPACT: Better communication, increased trust

DESIGN PHILOSOPHY:
    1. Professional appearance (publication-quality)
    2. Multiple formats (heatmaps, overlays, side-by-side)
    3. Customizable (colors, transparency, labels)
    4. Medical context (anatomical labels, severity)

PROS:
    ✅ Professional visualizations
    ✅ Multiple visualization types
    ✅ Customizable appearance
    ✅ Easy to use

CONS:
    ❌ Requires matplotlib/seaborn
    ❌ May need tuning for specific cases
    ❌ File size can be large for high-res

USAGE:
    from src.explainability.visualization import (
        overlay_heatmap,
        create_explanation_panel
    )
    
    # Overlay heatmap on image
    result = overlay_heatmap(
        image,
        heatmap,
        alpha=0.4,
        colormap='jet'
    )
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


def overlay_heatmap(
    image: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.4,
    colormap: str = 'jet',
    normalize: bool = True
) -> np.ndarray:
    """
    Overlay heatmap on image
    
    WHY OVERLAY:
        Heatmap alone: No context
        Image alone: No explanation
        Overlay: Best of both worlds
    
    WHY ALPHA BLENDING:
        Shows both image and heatmap
        Adjustable emphasis
        Standard visualization technique
    
    Args:
        image: Original image (H, W) or (H, W, 3)
        heatmap: Heatmap to overlay (H, W)
        alpha: Transparency of heatmap (0-1)
        colormap: Matplotlib colormap name
        normalize: Whether to normalize heatmap
        
    Returns:
        Overlaid image (H, W, 3)
    """
    # Ensure image is RGB
    # WHY RGB:
    # Consistent format for visualization
    # Color heatmaps require RGB
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # Normalize heatmap
    # WHY NORMALIZE:
    # Ensures full color range is used
    # Makes visualization more informative
    if normalize:
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)
    
    # Resize heatmap if needed
    # WHY RESIZE:
    # Heatmap and image must have same dimensions
    # Interpolation for smooth appearance
    if heatmap.shape != image.shape[:2]:
        heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
    
    # Apply colormap
    # WHY COLORMAP:
    # Maps scalar values to colors
    # 'jet': Red=high, Blue=low (intuitive)
    heatmap_colored = cv2.applyColorMap(
        np.uint8(255 * heatmap),
        getattr(cv2, f'COLORMAP_{colormap.upper()}')
    )
    
    # Blend
    # WHY ADDWEIGHTED:
    # Efficient alpha blending
    # Preserves both image and heatmap information
    overlay = cv2.addWeighted(image, 1 - alpha, heatmap_colored, alpha, 0)
    
    return overlay


def create_explanation_panel(
    original_image: np.ndarray,
    heatmap: np.ndarray,
    prediction: str,
    confidence: float,
    title: str = "Model Explanation",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create comprehensive explanation panel
    
    WHY PANEL:
        Multiple views provide complete picture
        Professional presentation
        Suitable for reports
    
    PANEL LAYOUT:
        [Original Image] [Heatmap] [Overlay]
        [Prediction and Confidence Info]
    
    Args:
        original_image: Original X-ray image
        heatmap: Explanation heatmap
        prediction: Model prediction
        confidence: Prediction confidence
        title: Panel title
        save_path: Path to save figure
        
    Returns:
        Matplotlib figure
    """
    # Create figure
    # WHY 3 COLUMNS:
    # Original: See input
    # Heatmap: See explanation
    # Overlay: See both together
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Original image
    # WHY GRAYSCALE:
    # X-rays are grayscale
    # Consistent with medical imaging
    axes[0].imshow(original_image, cmap='gray')
    axes[0].set_title('Original X-Ray', fontsize=12, fontweight='bold')
    axes[0].axis('off')
    
    # Heatmap
    # WHY JET COLORMAP:
    # Red = high importance (fracture location)
    # Blue = low importance
    # Intuitive for medical professionals
    im = axes[1].imshow(heatmap, cmap='jet')
    axes[1].set_title('Explanation Heatmap', fontsize=12, fontweight='bold')
    axes[1].axis('off')
    
    # Add colorbar
    # WHY COLORBAR:
    # Shows scale of importance
    # Enables quantitative interpretation
    plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
    
    # Overlay
    overlay = overlay_heatmap(original_image, heatmap)
    axes[2].imshow(overlay)
    axes[2].set_title('Overlay', fontsize=12, fontweight='bold')
    axes[2].axis('off')
    
    # Add prediction info
    # WHY INFO BOX:
    # Context for explanation
    # Shows what model predicted
    info_text = f"Prediction: {prediction}\nConfidence: {confidence:.1%}"
    fig.text(
        0.5, 0.02,
        info_text,
        ha='center',
        fontsize=14,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    # Main title
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved explanation panel to {save_path}")
    
    return fig


def create_comparison_panel(
    images: List[np.ndarray],
    heatmaps: List[np.ndarray],
    labels: List[str],
    title: str = "Model Comparison",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create comparison panel for multiple cases
    
    WHY COMPARISON:
        Shows model behavior across cases
        Identifies patterns
        Educational tool
    
    Args:
        images: List of images
        heatmaps: List of heatmaps
        labels: List of labels
        title: Panel title
        save_path: Path to save figure
        
    Returns:
        Matplotlib figure
    """
    n = len(images)
    fig, axes = plt.subplots(2, n, figsize=(5*n, 10))
    
    for i in range(n):
        # Original image
        axes[0, i].imshow(images[i], cmap='gray')
        axes[0, i].set_title(f'{labels[i]} - Original', fontweight='bold')
        axes[0, i].axis('off')
        
        # Overlay
        overlay = overlay_heatmap(images[i], heatmaps[i])
        axes[1, i].imshow(overlay)
        axes[1, i].set_title(f'{labels[i]} - Explanation', fontweight='bold')
        axes[1, i].axis('off')
    
    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved comparison panel to {save_path}")
    
    return fig


__all__ = [
    'overlay_heatmap',
    'create_explanation_panel',
    'create_comparison_panel'
]
