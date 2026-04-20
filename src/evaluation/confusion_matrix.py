"""
Confusion Matrix Utilities

PURPOSE:
    Creates and visualizes confusion matrices for model evaluation.
    Essential for understanding model errors and biases.

WHY CONFUSION MATRIX:
    Single accuracy number: Hides important details
    Confusion matrix (this): Shows exactly where model fails
    
    IMPACT: Better error analysis, targeted improvements

DESIGN PHILOSOPHY:
    1. Clear visualization (easy to interpret)
    2. Multiple formats (normalized, counts)
    3. Medical context (highlight dangerous errors)
    4. Export capabilities (save for reports)

PROS:
    ✅ Clear error visualization
    ✅ Identifies systematic biases
    ✅ Multiple normalization options
    ✅ Beautiful plots

CONS:
    ❌ Only for binary/multi-class (not regression)
    ❌ Can be misleading if classes very imbalanced
    ❌ Requires matplotlib for visualization

USAGE:
    from src.evaluation.confusion_matrix import plot_confusion_matrix
    
    plot_confusion_matrix(
        y_true=[1, 0, 1, 1, 0],
        y_pred=[1, 0, 1, 0, 0],
        classes=['Normal', 'Fracture'],
        normalize=True,
        save_path='confusion_matrix.png'
    )
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def plot_confusion_matrix(
    y_true: Union[List, np.ndarray],
    y_pred: Union[List, np.ndarray],
    classes: List[str] = ['Normal', 'Fracture'],
    normalize: bool = False,
    title: str = 'Confusion Matrix',
    cmap: str = 'Blues',
    save_path: Optional[str] = None,
    figsize: tuple = (8, 6)
):
    """
    Plot confusion matrix
    
    WHY VISUALIZE:
        Numbers alone are hard to interpret
        Heatmap shows patterns clearly
        Colors highlight problems
    
    WHY NORMALIZE:
        Raw counts: Biased by class sizes
        Normalized: Shows true error rates
        Both useful for different purposes
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        classes: Class names
        normalize: Whether to normalize by true labels
        title: Plot title
        cmap: Color map
        save_path: Path to save figure
        figsize: Figure size
    """
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    if normalize:
        # WHY NORMALIZE BY ROW (true labels):
        # Shows what % of each true class was predicted as each class
        # More interpretable for medical AI
        # Example: "90% of fractures correctly identified"
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        fmt = '.2%'
    else:
        fmt = 'd'
    
    # Create figure
    plt.figure(figsize=figsize)
    
    # WHY SEABORN HEATMAP:
    # Beautiful, professional appearance
    # Automatic color scaling
    # Easy annotations
    sns.heatmap(
        cm,
        annot=True,  # WHY: Show numbers in cells
        fmt=fmt,
        cmap=cmap,
        xticklabels=classes,
        yticklabels=classes,
        cbar=True,  # WHY: Color scale reference
        square=True  # WHY: Square cells look better
    )
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    
    # WHY TIGHT LAYOUT:
    # Prevents label cutoff
    # Professional appearance
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved confusion matrix to {save_path}")
    
    plt.show()


def analyze_confusion_matrix(
    y_true: Union[List, np.ndarray],
    y_pred: Union[List, np.ndarray],
    class_names: List[str] = ['Normal', 'Fracture']
) -> dict:
    """
    Analyze confusion matrix and provide insights
    
    WHY ANALYZE:
        Raw matrix doesn't tell the full story
        Need to interpret what errors mean
        Provide actionable insights
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        class_names: Class names
        
    Returns:
        Dictionary of insights
    """
    cm = confusion_matrix(y_true, y_pred)
    
    # For binary classification
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        
        insights = {
            'total_samples': len(y_true),
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        }
        
        # WHY THESE INSIGHTS:
        # Highlight dangerous errors
        # Provide context for numbers
        # Actionable recommendations
        
        if fn > 0:
            insights['false_negative_warning'] = (
                f"⚠️  CRITICAL: {fn} fractures missed! "
                f"This could lead to untreated injuries."
            )
        
        if fp > tp:
            insights['false_positive_warning'] = (
                f"⚠️  High false alarm rate: {fp} false positives vs {tp} true positives. "
                f"May reduce clinical trust."
            )
        
        # Calculate rates
        total_positives = tp + fn
        total_negatives = tn + fp
        
        if total_positives > 0:
            insights['sensitivity'] = tp / total_positives
        if total_negatives > 0:
            insights['specificity'] = tn / total_negatives
        
        return insights
    
    else:
        # Multi-class
        return {
            'confusion_matrix': cm.tolist(),
            'class_names': class_names,
            'total_samples': len(y_true)
        }


__all__ = [
    'plot_confusion_matrix',
    'analyze_confusion_matrix'
]
