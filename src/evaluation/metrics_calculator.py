"""
Metrics Calculator for Model Evaluation

PURPOSE:
    Calculates comprehensive evaluation metrics for medical AI models.
    Provides both standard ML metrics and medical-specific metrics.

WHY METRICS CALCULATOR:
    Manual calculation: Error-prone, inconsistent
    This calculator: Standardized, validated, comprehensive
    
    IMPACT: Reliable model evaluation, better decisions

DESIGN PHILOSOPHY:
    1. Medical relevance (sensitivity > accuracy)
    2. Comprehensive (multiple perspectives)
    3. Interpretable (clear clinical meaning)
    4. Validated (tested against known values)

PROS:
    ✅ Comprehensive metric suite
    ✅ Medical AI focused
    ✅ Handles edge cases
    ✅ Clear reporting

CONS:
    ❌ Can be overwhelming (many metrics)
    ❌ Requires understanding of metrics
    ❌ Computation overhead for large datasets

ALTERNATIVES:
    1. sklearn.metrics: Good but not medical-focused
    2. Custom calculations: Flexible but error-prone
    3. This calculator: Medical AI optimized

USAGE:
    from src.evaluation.metrics_calculator import MetricsCalculator
    
    calculator = MetricsCalculator()
    metrics = calculator.calculate_all_metrics(
        y_true=[1, 0, 1, 1, 0],
        y_pred=[1, 0, 1, 0, 0],
        y_prob=[0.9, 0.1, 0.95, 0.6, 0.2]
    )
    
    calculator.print_report(metrics)
"""

import numpy as np
from typing import Dict, List, Union, Optional, Tuple
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix as sklearn_confusion_matrix,
    classification_report
)
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Comprehensive metrics calculator for medical AI"""
    
    def __init__(self):
        """Initialize metrics calculator"""
        logger.info("Initialized MetricsCalculator")
    
    def calculate_all_metrics(
        self,
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray],
        y_prob: Optional[Union[List, np.ndarray]] = None,
        threshold: float = 0.5
    ) -> Dict[str, float]:
        """
        Calculate all evaluation metrics
        
        WHY ALL METRICS:
            Single metric is incomplete
            Different metrics reveal different aspects
            Medical AI needs comprehensive evaluation
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            y_prob: Predicted probabilities (optional)
            threshold: Classification threshold
            
        Returns:
            Dictionary of all metrics
        """
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # WHY VALIDATE:
        # Catch errors early
        # Provide clear error messages
        if len(y_true) != len(y_pred):
            raise ValueError(f"Length mismatch: y_true={len(y_true)}, y_pred={len(y_pred)}")
        
        metrics = {}
        
        # Standard ML metrics
        metrics.update(self._calculate_standard_metrics(y_true, y_pred))
        
        # Medical-specific metrics
        metrics.update(self._calculate_medical_metrics(y_true, y_pred))
        
        # Probability-based metrics
        if y_prob is not None:
            metrics.update(self._calculate_probability_metrics(y_true, y_prob))
        
        # Confusion matrix components
        metrics.update(self._calculate_confusion_components(y_true, y_pred))
        
        logger.info(f"Calculated {len(metrics)} metrics")
        
        return metrics
    
    def _calculate_standard_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate standard ML metrics
        
        WHY THESE METRICS:
            Accuracy: Overall correctness
            Precision: Positive prediction reliability
            Recall: Positive detection rate
            F1: Harmonic mean of precision/recall
        """
        return {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0)
        }
    
    def _calculate_medical_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate medical AI-specific metrics
        
        WHY MEDICAL METRICS:
            Clinically meaningful
            Safety-focused
            Standard in medical literature
        """
        # Get confusion matrix
        tn, fp, fn, tp = sklearn_confusion_matrix(y_true, y_pred).ravel()
        
        # WHY SENSITIVITY (RECALL):
        # Most critical for medical AI
        # Measures ability to detect fractures
        # High sensitivity = fewer missed fractures
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        # WHY SPECIFICITY:
        # Ability to correctly identify normal cases
        # High specificity = fewer false alarms
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        
        # WHY PPV (PRECISION):
        # When model says "fracture", how often is it right?
        # Critical for clinical trust
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        
        # WHY NPV:
        # When model says "normal", how often is it right?
        # Important for ruling out fractures
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
        
        # WHY FALSE NEGATIVE RATE:
        # Most dangerous error in medical AI
        # Missed fractures can lead to complications
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        
        # WHY FALSE POSITIVE RATE:
        # Unnecessary worry and treatment
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        
        return {
            'sensitivity': sensitivity,
            'specificity': specificity,
            'ppv': ppv,
            'npv': npv,
            'false_negative_rate': fnr,
            'false_positive_rate': fpr
        }
    
    def _calculate_probability_metrics(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate probability-based metrics
        
        WHY PROBABILITY METRICS:
            AUC-ROC: Overall discrimination ability
            AP: Precision-recall trade-off
            Threshold-independent evaluation
        """
        metrics = {}
        
        try:
            # WHY AUC-ROC:
            # Threshold-independent
            # Shows overall discrimination
            # Standard in ML
            metrics['auc_roc'] = roc_auc_score(y_true, y_prob)
        except ValueError as e:
            logger.warning(f"Could not calculate AUC-ROC: {e}")
            metrics['auc_roc'] = 0.0
        
        try:
            # WHY AVERAGE PRECISION:
            # Better for imbalanced datasets
            # Focuses on positive class
            # Useful for medical AI
            metrics['average_precision'] = average_precision_score(y_true, y_prob)
        except ValueError as e:
            logger.warning(f"Could not calculate AP: {e}")
            metrics['average_precision'] = 0.0
        
        return metrics
    
    def _calculate_confusion_components(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, int]:
        """
        Calculate confusion matrix components
        
        WHY CONFUSION MATRIX:
            Foundation for all other metrics
            Clear visualization of errors
            Essential for medical AI
        """
        tn, fp, fn, tp = sklearn_confusion_matrix(y_true, y_pred).ravel()
        
        return {
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        }
    
    def print_report(
        self,
        metrics: Dict[str, float],
        title: str = "Model Evaluation Report"
    ):
        """
        Print formatted metrics report
        
        WHY FORMATTED REPORT:
            Raw numbers are hard to interpret
            Formatted output is more readable
            Highlights critical metrics
        """
        print(f"\n{'='*70}")
        print(f"{title:^70}")
        print(f"{'='*70}\n")
        
        print("📊 Standard ML Metrics:")
        print(f"  Accuracy:  {metrics.get('accuracy', 0):.2%}")
        print(f"  Precision: {metrics.get('precision', 0):.2%}")
        print(f"  Recall:    {metrics.get('recall', 0):.2%}")
        print(f"  F1 Score:  {metrics.get('f1_score', 0):.2%}")
        
        if 'auc_roc' in metrics:
            print(f"\n📈 Probability Metrics:")
            print(f"  AUC-ROC:           {metrics.get('auc_roc', 0):.2%}")
            print(f"  Average Precision: {metrics.get('average_precision', 0):.2%}")
        
        print(f"\n🏥 Medical AI Metrics (Critical for Patient Safety):")
        print(f"  Sensitivity (Recall):     {metrics.get('sensitivity', 0):.2%}  ← Catch fractures")
        print(f"  Specificity:              {metrics.get('specificity', 0):.2%}  ← Avoid false alarms")
        print(f"  PPV (Precision):          {metrics.get('ppv', 0):.2%}  ← Positive reliability")
        print(f"  NPV:                      {metrics.get('npv', 0):.2%}  ← Negative reliability")
        
        print(f"\n⚠️  Error Analysis:")
        print(f"  False Negative Rate:      {metrics.get('false_negative_rate', 0):.2%}  🚨 CRITICAL")
        print(f"  False Positive Rate:      {metrics.get('false_positive_rate', 0):.2%}")
        
        print(f"\n📋 Confusion Matrix:")
        print(f"  True Positives:   {metrics.get('true_positives', 0)}")
        print(f"  True Negatives:   {metrics.get('true_negatives', 0)}")
        print(f"  False Positives:  {metrics.get('false_positives', 0)}")
        print(f"  False Negatives:  {metrics.get('false_negatives', 0)}  🚨 MONITOR CLOSELY")
        
        print(f"\n{'='*70}\n")


__all__ = ['MetricsCalculator']
