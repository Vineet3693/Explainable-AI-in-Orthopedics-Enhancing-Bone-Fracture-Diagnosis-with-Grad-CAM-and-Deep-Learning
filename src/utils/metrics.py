"""
Metrics Calculation Utilities

PURPOSE:
    Calculate evaluation metrics for model performance assessment.
    Provides medical AI-specific metrics (sensitivity, specificity, PPV, NPV).

WHY MEDICAL METRICS:
    Standard accuracy: Misleading for imbalanced medical data
    Medical metrics (this): Clinically meaningful, safety-focused
    
    IMPACT: Better model evaluation, patient safety

DESIGN PHILOSOPHY:
    1. Medical relevance (sensitivity > accuracy)
    2. Interpretability (clear clinical meaning)
    3. Comprehensive (multiple complementary metrics)
    4. Safety-first (prioritize false negative detection)

PROS:
    ✅ Clinically meaningful metrics
    ✅ Handles class imbalance
    ✅ Multiple perspectives (sensitivity, specificity, PPV, NPV)
    ✅ Safety-focused (tracks false negatives)

CONS:
    ❌ More complex than simple accuracy
    ❌ Requires understanding of medical context
    ❌ Multiple metrics can be confusing

ALTERNATIVES:
    1. Simple accuracy: Easy but misleading for medical AI
    2. F1 score: Good but less interpretable clinically
    3. AUC-ROC: Great for threshold selection but abstract
    
COMPARISON:
    | Metric        | Clinical Meaning | Imbalance-Robust | Interpretable | Safety-Focus |
    |---------------|------------------|------------------|---------------|--------------|
    | Accuracy      | ❌               | ❌               | ✅            | ❌           |
    | F1 Score      | ⚠️               | ✅               | ⚠️            | ⚠️           |
    | AUC-ROC       | ❌               | ✅               | ❌            | ⚠️           |
    | Sensitivity   | ✅               | ✅               | ✅            | ✅           |
    | This (all)    | ✅               | ✅               | ✅            | ✅           |

USAGE:
    from src.utils.metrics import calculate_metrics
    
    metrics = calculate_metrics(
        y_true=[1, 0, 1, 1, 0],
        y_pred=[1, 0, 1, 0, 0]
    )
    print(f"Sensitivity: {metrics['sensitivity']:.2%}")
"""

from typing import Dict, List, Union
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score
)
import logging

logger = logging.getLogger(__name__)


def calculate_metrics(
    y_true: Union[List, np.ndarray],
    y_pred: Union[List, np.ndarray],
    y_prob: Union[List, np.ndarray, None] = None
) -> Dict[str, float]:
    """
    Calculate comprehensive evaluation metrics
    
    WHY MULTIPLE METRICS:
        Single metric gives incomplete picture
        Different metrics reveal different aspects
        Medical AI needs comprehensive evaluation
    
    WHY THESE SPECIFIC METRICS:
        - Sensitivity (Recall): Catch fractures (critical for patient safety)
        - Specificity: Avoid false alarms (reduce unnecessary treatment)
        - PPV (Precision): Positive prediction reliability
        - NPV: Negative prediction reliability
        - F1: Balance between precision and recall
        - AUC: Overall discrimination ability
    
    Args:
        y_true: Ground truth labels (0 or 1)
        y_pred: Predicted labels (0 or 1)
        y_prob: Predicted probabilities (optional, for AUC)
        
    Returns:
        Dictionary of metrics
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # WHY VALIDATE INPUTS:
    # Prevent silent errors from shape mismatches
    # Fail fast with clear error message
    if len(y_true) != len(y_pred):
        raise ValueError(f"Length mismatch: y_true={len(y_true)}, y_pred={len(y_pred)}")
    
    # Calculate confusion matrix
    # WHY CONFUSION MATRIX FIRST:
    # All other metrics derive from it
    # More efficient to calculate once
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
    }
    
    # Medical-specific metrics
    # WHY SENSITIVITY (RECALL):
    # Most critical for medical AI
    # Measures ability to catch fractures
    # High sensitivity = fewer missed fractures
    metrics['sensitivity'] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    # WHY SPECIFICITY:
    # Measures ability to correctly identify normal cases
    # High specificity = fewer false alarms
    # Important for reducing unnecessary interventions
    metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    # WHY PPV (POSITIVE PREDICTIVE VALUE):
    # When model says "fracture", how often is it right?
    # Critical for clinical trust
    metrics['ppv'] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    # WHY NPV (NEGATIVE PREDICTIVE VALUE):
    # When model says "normal", how often is it right?
    # Important for ruling out fractures
    metrics['npv'] = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    
    # WHY FALSE NEGATIVE RATE:
    # Most dangerous error in medical AI
    # Missed fractures can lead to complications
    # Must be monitored closely
    metrics['false_negative_rate'] = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    
    # WHY FALSE POSITIVE RATE:
    # Unnecessary worry and treatment
    # Less critical than FN but still important
    metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    
    # Confusion matrix components
    metrics['true_positives'] = int(tp)
    metrics['true_negatives'] = int(tn)
    metrics['false_positives'] = int(fp)
    metrics['false_negatives'] = int(fn)
    
    # AUC if probabilities provided
    # WHY AUC:
    # Threshold-independent metric
    # Useful for comparing models
    # Shows overall discrimination ability
    if y_prob is not None:
        try:
            metrics['auc_roc'] = roc_auc_score(y_true, y_prob)
        except ValueError as e:
            logger.warning(f"Could not calculate AUC: {e}")
            metrics['auc_roc'] = 0.0
    
    return metrics


def print_metrics_report(metrics: Dict[str, float], title: str = "Evaluation Metrics"):
    """
    Print formatted metrics report
    
    WHY FORMATTED REPORT:
        Raw numbers are hard to interpret
        Formatted output is more readable
        Highlights critical metrics
    
    Args:
        metrics: Dictionary of metrics
        title: Report title
    """
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}\n")
    
    # WHY GROUP METRICS:
    # Logical organization aids understanding
    # Related metrics shown together
    
    print("Overall Performance:")
    print(f"  Accuracy:  {metrics.get('accuracy', 0):.2%}")
    print(f"  F1 Score:  {metrics.get('f1', 0):.2%}")
    if 'auc_roc' in metrics:
        print(f"  AUC-ROC:   {metrics.get('auc_roc', 0):.2%}")
    
    print("\nMedical Metrics (Critical for Patient Safety):")
    print(f"  Sensitivity (Recall):     {metrics.get('sensitivity', 0):.2%}  ← Catch fractures")
    print(f"  Specificity:              {metrics.get('specificity', 0):.2%}  ← Avoid false alarms")
    print(f"  PPV (Precision):          {metrics.get('ppv', 0):.2%}  ← Positive reliability")
    print(f"  NPV:                      {metrics.get('npv', 0):.2%}  ← Negative reliability")
    
    print("\nError Analysis:")
    print(f"  False Negative Rate:      {metrics.get('false_negative_rate', 0):.2%}  ⚠️  CRITICAL")
    print(f"  False Positive Rate:      {metrics.get('false_positive_rate', 0):.2%}")
    
    print("\nConfusion Matrix:")
    print(f"  True Positives:   {metrics.get('true_positives', 0)}")
    print(f"  True Negatives:   {metrics.get('true_negatives', 0)}")
    print(f"  False Positives:  {metrics.get('false_positives', 0)}")
    print(f"  False Negatives:  {metrics.get('false_negatives', 0)}  ⚠️  MONITOR CLOSELY")
    
    print(f"\n{'='*60}\n")


__all__ = [
    'calculate_metrics',
    'print_metrics_report'
]
