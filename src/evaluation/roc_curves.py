"""
ROC and Precision-Recall Curves

PURPOSE:
    Generates ROC and PR curves for threshold selection and model comparison.
    Essential for understanding model performance across different operating points.

WHY ROC/PR CURVES:
    Single threshold: May not be optimal
    Curves (this): Show performance across all thresholds
    
    IMPACT: Better threshold selection, informed decisions

DESIGN PHILOSOPHY:
    1. Threshold-independent evaluation
    2. Multiple curves for comparison
    3. Optimal point identification
    4. Medical context (prioritize sensitivity)

PROS:
    ✅ Threshold-independent
    ✅ Visual comparison of models
    ✅ Identifies optimal operating point
    ✅ Standard in ML literature

CONS:
    ❌ Can be misleading for imbalanced data (ROC)
    ❌ Requires probability predictions
    ❌ May be complex for non-technical stakeholders

ALTERNATIVES:
    1. Single threshold evaluation: Simple but limited
    2. ROC curve only: Good but misleading for imbalance
    3. PR curve only: Better for imbalance but less standard
    4. Both (this): Comprehensive view

USAGE:
    from src.evaluation.roc_curves import plot_roc_curve, plot_pr_curve
    
    plot_roc_curve(
        y_true=[1, 0, 1, 1, 0],
        y_prob=[0.9, 0.1, 0.95, 0.6, 0.2],
        save_path='roc_curve.png'
    )
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score
)
from typing import List, Union, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def plot_roc_curve(
    y_true: Union[List, np.ndarray],
    y_prob: Union[List, np.ndarray],
    title: str = 'ROC Curve',
    save_path: Optional[str] = None,
    figsize: tuple = (8, 6)
):
    """
    Plot ROC (Receiver Operating Characteristic) curve
    
    WHY ROC CURVE:
        Shows trade-off between TPR and FPR
        Threshold-independent evaluation
        AUC summarizes overall performance
    
    WHY TPR vs FPR:
        TPR (sensitivity): Catch fractures
        FPR: False alarms
        Trade-off is fundamental to classification
    
    Args:
        y_true: Ground truth labels
        y_prob: Predicted probabilities
        title: Plot title
        save_path: Path to save figure
        figsize: Figure size
    """
    # Calculate ROC curve
    # WHY THESE OUTPUTS:
    # fpr: False positive rates at different thresholds
    # tpr: True positive rates at different thresholds
    # thresholds: Decision thresholds
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    
    # Calculate AUC
    # WHY AUC:
    # Single number summary of ROC curve
    # 0.5 = random, 1.0 = perfect
    # Standard metric for comparison
    roc_auc = auc(fpr, tpr)
    
    # Create plot
    plt.figure(figsize=figsize)
    
    # Plot ROC curve
    plt.plot(
        fpr, tpr,
        color='darkorange',
        lw=2,
        label=f'ROC curve (AUC = {roc_auc:.3f})'
    )
    
    # Plot diagonal (random classifier)
    # WHY DIAGONAL:
    # Shows performance of random guessing
    # Anything above is better than random
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
    
    # Find optimal threshold (Youden's J statistic)
    # WHY YOUDEN'S J:
    # Maximizes (sensitivity + specificity - 1)
    # Balances both metrics
    # Good default for medical AI
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[optimal_idx]
    
    # Mark optimal point
    plt.plot(
        fpr[optimal_idx], tpr[optimal_idx],
        'ro',
        markersize=10,
        label=f'Optimal (threshold={optimal_threshold:.3f})'
    )
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate (Sensitivity)', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved ROC curve to {save_path}")
    
    plt.show()
    
    return {
        'auc': roc_auc,
        'optimal_threshold': optimal_threshold,
        'optimal_tpr': tpr[optimal_idx],
        'optimal_fpr': fpr[optimal_idx]
    }


def plot_pr_curve(
    y_true: Union[List, np.ndarray],
    y_prob: Union[List, np.ndarray],
    title: str = 'Precision-Recall Curve',
    save_path: Optional[str] = None,
    figsize: tuple = (8, 6)
):
    """
    Plot Precision-Recall curve
    
    WHY PR CURVE:
        Better for imbalanced datasets
        Focuses on positive class
        More informative for medical AI
    
    WHY BETTER FOR IMBALANCE:
        ROC can be optimistic with imbalance
        PR curve shows true positive class performance
        Critical when fractures are rare
    
    Args:
        y_true: Ground truth labels
        y_prob: Predicted probabilities
        title: Plot title
        save_path: Path to save figure
        figsize: Figure size
    """
    # Calculate PR curve
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    
    # Calculate average precision
    # WHY AVERAGE PRECISION:
    # Summary metric for PR curve
    # Weighted mean of precisions
    # Better than AUC for imbalanced data
    avg_precision = average_precision_score(y_true, y_prob)
    
    # Create plot
    plt.figure(figsize=figsize)
    
    # Plot PR curve
    plt.plot(
        recall, precision,
        color='darkorange',
        lw=2,
        label=f'PR curve (AP = {avg_precision:.3f})'
    )
    
    # Plot baseline (random classifier)
    # WHY BASELINE:
    # For imbalanced data, random is not 0.5
    # Baseline = proportion of positive class
    baseline = np.sum(y_true) / len(y_true)
    plt.plot([0, 1], [baseline, baseline], color='navy', lw=2, linestyle='--', label=f'Random (AP = {baseline:.3f})')
    
    # Find optimal threshold (F1 score)
    # WHY F1:
    # Harmonic mean of precision and recall
    # Balances both metrics
    # Standard for imbalanced data
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-10)
    optimal_idx = np.argmax(f1_scores)
    optimal_threshold = thresholds[optimal_idx]
    
    # Mark optimal point
    plt.plot(
        recall[optimal_idx], precision[optimal_idx],
        'ro',
        markersize=10,
        label=f'Optimal (threshold={optimal_threshold:.3f})'
    )
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall (Sensitivity)', fontsize=12)
    plt.ylabel('Precision (PPV)', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend(loc="lower left")
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved PR curve to {save_path}")
    
    plt.show()
    
    return {
        'average_precision': avg_precision,
        'optimal_threshold': optimal_threshold,
        'optimal_precision': precision[optimal_idx],
        'optimal_recall': recall[optimal_idx]
    }


__all__ = [
    'plot_roc_curve',
    'plot_pr_curve'
]
