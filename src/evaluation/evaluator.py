"""
Model evaluator for fracture detection

PURPOSE:
    Calculates comprehensive evaluation metrics for trained models with focus
    on medical AI requirements. Goes beyond accuracy to include sensitivity,
    specificity, false negative rate, and other clinically relevant metrics.

WHY COMPREHENSIVE EVALUATION MATTERS:
    Accuracy alone: Can be misleading (90% accuracy but misses all fractures!)
    Comprehensive metrics: True understanding of model performance
    
    IMPACT: Prevents deployment of dangerous models, ensures patient safety

DESIGN PHILOSOPHY:
    1. Medical metrics first (sensitivity > accuracy)
    2. Patient safety focus (FN rate is critical)
    3. Comprehensive reporting (not just one number)
    4. Actionable insights (what to improve)

MEDICAL AI METRICS (in order of importance):

1. RECALL/SENSITIVITY (Most Important!)
   - What % of fractures did we catch?
   - TARGET: >95% (miss <5% of fractures)
   - WHY CRITICAL: Missing a fracture can harm patient
   - TRADE-OFF: May increase false alarms

2. FALSE NEGATIVE RATE
   - What % of fractures did we miss?
   - TARGET: <5% (catch >95% of fractures)
   - WHY CRITICAL: Direct patient safety metric
   - INVERSE: 1 - Recall

3. SPECIFICITY
   - What % of normal X-rays did we correctly identify?
   - TARGET: >85% (avoid too many false alarms)
   - WHY IMPORTANT: Reduces unnecessary worry/treatment
   - TRADE-OFF: Lower = more false alarms

4. PRECISION
   - Of our "fracture" predictions, what % were correct?
   - TARGET: >90%
   - WHY IMPORTANT: Reduces false alarms
   - TRADE-OFF: Can be high by being conservative

5. F1-SCORE
   - Harmonic mean of precision and recall
   - TARGET: >92%
   - WHY USEFUL: Balances precision and recall
   - LIMITATION: Doesn't weight FN vs FP

6. AUC-ROC
   - Area under ROC curve
   - TARGET: >0.95
   - WHY USEFUL: Threshold-independent performance
   - LIMITATION: Can be misleading with class imbalance

7. ACCURACY
   - Overall correct predictions
   - TARGET: >90%
   - WHY LEAST IMPORTANT: Can be misleading with imbalance
   - EXAMPLE: 95% accuracy but 50% recall is BAD

PROS:
    ✅ Comprehensive medical metrics
    ✅ Patient safety focus
    ✅ Identifies model weaknesses
    ✅ Actionable insights
    ✅ Confusion matrix analysis
    ✅ Misclassified sample tracking

CONS:
    ❌ More complex than simple accuracy
    ❌ Requires understanding of metrics
    ❌ May be overwhelming for non-experts

ALTERNATIVES:
    1. Accuracy only: Simple but dangerous for medical AI
    2. Precision/Recall only: Insufficient
    3. This approach: Comprehensive, medical-focused
    4. Custom medical metrics: More complex

COMPARISON:
    Approach            | Medical Safety | Completeness | Complexity
    Accuracy only       | ❌ Dangerous   | Low          | Low
    P/R only            | ⚠️ Partial    | Medium       | Low
    Comprehensive (this)| ✅ Safe        | High         | Medium
    Custom metrics      | ✅ Safe        | V.High       | High

HOW IT AFFECTS APPLICATION:
    - Model selection: Choose safest model, not just most accurate
    - Deployment: Only deploy if all metrics meet thresholds
    - Monitoring: Track all metrics in production
    - Improvement: Know exactly what to improve
    - Compliance: Audit trail for medical AI

PERFORMANCE:
    - Evaluation time: ~10-30 seconds for 1000 images
    - Memory: Minimal
    - Computation: CPU is sufficient

MEDICAL AI CONSIDERATIONS:
    - Recall > Precision (missing fracture worse than false alarm)
    - False negatives are critical (patient safety)
    - Confusion matrix shows failure modes
    - Track misclassified samples for analysis
    - Report all metrics, not just best one

METRIC THRESHOLDS FOR DEPLOYMENT:
    REQUIRED (must meet all):
    - Recall/Sensitivity: ≥95%
    - False Negative Rate: ≤5%
    - Specificity: ≥85%
    
    DESIRED (should meet):
    - Precision: ≥90%
    - F1-Score: ≥92%
    - AUC-ROC: ≥0.95
    - Accuracy: ≥90%
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report
)
from typing import Dict, Tuple, List
import logging
import json

logger = logging.getLogger(__name__)


class Evaluator:
    """Comprehensive model evaluation"""
    
    def __init__(self, model):
        """
        Initialize evaluator
        
        Args:
            model: Trained Keras model
        """
        self.model = model
    
    def evaluate(
        self,
        test_data,
        threshold: float = 0.5
    ) -> Dict:
        """
        Comprehensive model evaluation
        
        Args:
            test_data: Test dataset
            threshold: Classification threshold
            
        Returns:
            Evaluation metrics dictionary
        """
        logger.info("Starting model evaluation...")
        
        # Get predictions
        y_pred_proba = self.model.predict(test_data, verbose=1)
        y_pred = (y_pred_proba > threshold).astype(int)
        
        # Get true labels
        y_true = np.concatenate([y for x, y in test_data], axis=0)
        
        # Calculate metrics
        metrics = self.calculate_metrics(y_true, y_pred, y_pred_proba)
        
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # Get classification report
        report = classification_report(y_true, y_pred, target_names=['Normal', 'Fractured'])
        metrics['classification_report'] = report
        
        logger.info("Evaluation completed!")
        logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f}")
        logger.info(f"Recall: {metrics['recall']:.4f}")
        logger.info(f"F1-Score: {metrics['f1_score']:.4f}")
        logger.info(f"AUC-ROC: {metrics['auc_roc']:.4f}")
        
        return metrics
    
    @staticmethod
    def calculate_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray
    ) -> Dict:
        """
        Calculate all evaluation metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities
            
        Returns:
            Metrics dictionary
        """
        return {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
            'auc_roc': float(roc_auc_score(y_true, y_pred_proba)),
            'specificity': float(Evaluator._calculate_specificity(y_true, y_pred)),
            'sensitivity': float(recall_score(y_true, y_pred, zero_division=0)),  # Same as recall
            'false_negative_rate': float(Evaluator._calculate_fnr(y_true, y_pred)),
            'false_positive_rate': float(Evaluator._calculate_fpr(y_true, y_pred))
        }
    
    @staticmethod
    def _calculate_specificity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate specificity (True Negative Rate)"""
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        return tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    @staticmethod
    def _calculate_fnr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate False Negative Rate (CRITICAL for medical AI)"""
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        return fn / (fn + tp) if (fn + tp) > 0 else 0.0
    
    @staticmethod
    def _calculate_fpr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate False Positive Rate"""
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        return fp / (fp + tn) if (fp + tn) > 0 else 0.0
    
    def get_misclassified_samples(
        self,
        test_data,
        threshold: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get indices of misclassified samples
        
        Args:
            test_data: Test dataset
            threshold: Classification threshold
            
        Returns:
            (false_negative_indices, false_positive_indices)
        """
        # Get predictions
        y_pred_proba = self.model.predict(test_data, verbose=0)
        y_pred = (y_pred_proba > threshold).astype(int).flatten()
        
        # Get true labels
        y_true = np.concatenate([y for x, y in test_data], axis=0).flatten()
        
        # Find misclassified samples
        false_negatives = np.where((y_true == 1) & (y_pred == 0))[0]
        false_positives = np.where((y_true == 0) & (y_pred == 1))[0]
        
        logger.info(f"False Negatives: {len(false_negatives)}")
        logger.info(f"False Positives: {len(false_positives)}")
        
        return false_negatives, false_positives


if __name__ == "__main__":
    # Test evaluator
    from src.models.resnet50_model import ResNet50Model
    
    # Create dummy model
    model = ResNet50Model()
    model.build_model()
    
    evaluator = Evaluator(model.model)
    print("Evaluator created successfully")
