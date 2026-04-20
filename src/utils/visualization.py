"""
Visualization Utilities for Plotting and Charts

PURPOSE:
    Provides reusable plotting functions for training curves, confusion matrices,
    ROC curves, and other visualizations. Ensures consistent styling across
    all project visualizations.

WHY CENTRALIZED VISUALIZATION:
    Scattered plotting code: Inconsistent styles, duplicate code
    Centralized utilities: Consistent look, DRY principle
    
    IMPACT: Professional-looking plots, easier maintenance

DESIGN PHILOSOPHY:
    1. Consistent styling (colors, fonts, sizes)
    2. Publication-ready quality
    3. Easy to use (simple function calls)
    4. Flexible (customizable parameters)

KEY CONCEPTS:
    - Matplotlib: Python plotting library
    - Seaborn: Statistical visualization (built on matplotlib)
    - Figure/Axes: Matplotlib objects for plots
    - DPI: Dots per inch (resolution)
    - Colormap: Color scheme for heatmaps

PROS:
    ✅ Consistent styling across all plots
    ✅ Reusable code (DRY principle)
    ✅ Publication-ready quality
    ✅ Easy to customize
    ✅ Supports multiple plot types

CONS:
    ❌ Less flexibility than custom plotting
    ❌ Requires matplotlib/seaborn knowledge
    ❌ May not fit all use cases

ALTERNATIVES:
    1. Custom plots each time: Flexible but inconsistent
    2. Plotly: Interactive but heavier
    3. Matplotlib utils (this): Consistent, lightweight
    4. Seaborn only: Limited plot types

COMPARISON:
    Approach          | Consistency | Flexibility | Interactivity
    Custom each time  | Low         | High        | No
    Plotly            | Medium      | High        | Yes
    Utils (this)      | High        | Medium      | No
    Seaborn only      | High        | Low         | No

USAGE:
    from src.utils.visualization import plot_training_curves, plot_confusion_matrix
    
    # Plot training history
    plot_training_curves(history, save_path='training.png')
    
    # Plot confusion matrix
    plot_confusion_matrix(y_true, y_pred, save_path='confusion.png')
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Set consistent style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def plot_training_curves(
    history: dict,
    metrics: List[str] = ['loss', 'accuracy'],
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 5)
):
    """
    Plot training and validation curves
    
    WHY THIS FUNCTION:
        Visualizing training progress is essential for:
        - Detecting overfitting (train/val divergence)
        - Monitoring convergence
        - Comparing experiments
    
    Args:
        history: Training history dict from model.fit()
        metrics: List of metrics to plot
        save_path: Path to save figure (optional)
        figsize: Figure size (width, height)
    
    Example:
        >>> history = model.fit(train_data, validation_data=val_data, epochs=50)
        >>> plot_training_curves(history.history, save_path='training.png')
    """
    n_metrics = len(metrics)
    fig, axes = plt.subplots(1, n_metrics, figsize=figsize)
    
    if n_metrics == 1:
        axes = [axes]
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        
        # Plot training metric
        if metric in history:
            ax.plot(history[metric], label=f'Train {metric}', linewidth=2)
        
        # Plot validation metric
        val_metric = f'val_{metric}'
        if val_metric in history:
            ax.plot(history[val_metric], label=f'Val {metric}', linewidth=2)
        
        ax.set_xlabel('Epoch', fontsize=12)
        ax.set_ylabel(metric.capitalize(), fontsize=12)
        ax.set_title(f'{metric.capitalize()} over Epochs', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved training curves to {save_path}")
    
    plt.show()


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    classes: List[str] = ['Normal', 'Fracture'],
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 6)
):
    """
    Plot confusion matrix heatmap
    
    WHY CONFUSION MATRIX:
        Essential for medical AI to understand:
        - True Positives: Correctly detected fractures
        - False Negatives: Missed fractures (CRITICAL for patient safety)
        - False Positives: False alarms
        - True Negatives: Correctly identified normal X-rays
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        classes: Class names
        save_path: Path to save figure
        figsize: Figure size
    
    Example:
        >>> plot_confusion_matrix(y_test, y_pred, save_path='confusion.png')
    """
    from sklearn.metrics import confusion_matrix
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Create heatmap
    plt.figure(figsize=figsize)
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=classes,
        yticklabels=classes,
        cbar_kws={'label': 'Count'},
        square=True,
        linewidths=1,
        linecolor='gray'
    )
    
    plt.title('Confusion Matrix', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    
    # Add percentage annotations
    total = cm.sum()
    for i in range(len(classes)):
        for j in range(len(classes)):
            percentage = cm[i, j] / total * 100
            plt.text(
                j + 0.5, i + 0.7,
                f'({percentage:.1f}%)',
                ha='center',
                va='center',
                fontsize=9,
                color='gray'
            )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved confusion matrix to {save_path}")
    
    plt.show()


def plot_roc_curve(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 6)
):
    """
    Plot ROC curve with AUC score
    
    WHY ROC CURVE:
        Shows trade-off between sensitivity and specificity
        AUC (Area Under Curve) is a single metric for model quality
        Target: AUC > 0.95 for medical AI
    
    Args:
        y_true: True binary labels
        y_scores: Predicted probabilities
        save_path: Path to save figure
        figsize: Figure size
    """
    from sklearn.metrics import roc_curve, auc
    
    # Calculate ROC curve
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    
    # Plot
    plt.figure(figsize=figsize)
    plt.plot(
        fpr, tpr,
        color='darkorange',
        lw=2,
        label=f'ROC curve (AUC = {roc_auc:.3f})'
    )
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate (Sensitivity)', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved ROC curve to {save_path}")
    
    plt.show()


def plot_metrics_comparison(
    metrics_dict: dict,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6)
):
    """
    Plot bar chart comparing multiple metrics
    
    WHY METRICS COMPARISON:
        Quickly compare model performance across different metrics
        Essential for model selection and evaluation
    
    Args:
        metrics_dict: Dictionary of metric names and values
        save_path: Path to save figure
        figsize: Figure size
    
    Example:
        >>> metrics = {
        ...     'Accuracy': 0.94,
        ...     'Precision': 0.92,
        ...     'Recall': 0.96,
        ...     'F1-Score': 0.94,
        ...     'AUC': 0.97
        ... }
        >>> plot_metrics_comparison(metrics, save_path='metrics.png')
    """
    metrics = list(metrics_dict.keys())
    values = list(metrics_dict.values())
    
    plt.figure(figsize=figsize)
    bars = plt.bar(metrics, values, color='steelblue', alpha=0.8, edgecolor='black')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{height:.3f}',
            ha='center',
            va='bottom',
            fontsize=11,
            fontweight='bold'
        )
    
    plt.ylabel('Score', fontsize=12)
    plt.title('Model Performance Metrics', fontsize=14, fontweight='bold')
    plt.ylim([0, 1.1])
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved metrics comparison to {save_path}")
    
    plt.show()


__all__ = [
    'plot_training_curves',
    'plot_confusion_matrix',
    'plot_roc_curve',
    'plot_metrics_comparison'
]
