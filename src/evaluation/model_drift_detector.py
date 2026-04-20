"""
Model Drift Detector

PURPOSE:
    Detects model performance degradation over time.
    Monitors prediction quality and alerts when model needs retraining.

WHY MODEL DRIFT DETECTION:
    Models degrade: Data distribution changes, new fracture types
    Drift detection (this): Catch problems early, maintain quality
    
    IMPACT: Sustained accuracy, patient safety

DESIGN PHILOSOPHY:
    1. Multiple drift metrics (accuracy, confidence, predictions)
    2. Statistical significance testing
    3. Configurable thresholds
    4. Actionable alerts

PROS:
    ✅ Early problem detection
    ✅ Automated monitoring
    ✅ Prevents silent failures
    ✅ Triggers retraining

CONS:
    ❌ Requires baseline metrics
    ❌ May have false positives
    ❌ Needs labeled data for validation

COMPARISON:
    | Method              | Sensitivity | Specificity | Latency | Data Needed |
    |---------------------|-------------|-------------|---------|-------------|
    | Accuracy Drop       | Medium      | High        | High    | Labels      |
    | Confidence Shift    | High        | Medium      | Low     | None        |
    | Prediction Dist     | High        | Low         | Low     | None        |
    | Statistical Tests   | High        | High        | Medium  | Labels      |

USAGE:
    from src.evaluation.model_drift_detector import ModelDriftDetector
    
    detector = ModelDriftDetector(baseline_metrics)
    
    # Check for drift
    is_drift, report = detector.detect_drift(
        current_predictions,
        current_labels
    )
"""

import numpy as np
from typing import Dict, Tuple, List, Optional
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class ModelDriftDetector:
    """Detects model performance drift"""
    
    def __init__(
        self,
        baseline_metrics: Dict[str, float],
        threshold: float = 0.05
    ):
        """
        Initialize drift detector
        
        WHY BASELINE:
            Need reference point for comparison
            Typically from validation set
            Represents expected performance
        
        WHY THRESHOLD:
            0.05 = 5% accuracy drop triggers alert
            Medical AI: Low threshold for safety
            Adjustable based on requirements
        
        Args:
            baseline_metrics: Expected model performance
            threshold: Acceptable performance drop (0-1)
        """
        self.baseline_metrics = baseline_metrics
        self.threshold = threshold
        
        logger.info(
            f"Initialized ModelDriftDetector "
            f"(threshold={threshold:.1%})"
        )
    
    def detect_drift(
        self,
        predictions: np.ndarray,
        labels: np.ndarray,
        probabilities: Optional[np.ndarray] = None
    ) -> Tuple[bool, Dict]:
        """
        Detect model drift
        
        WHY MULTIPLE SIGNALS:
            Accuracy alone may miss issues
            Confidence changes indicate problems
            Prediction distribution shifts
            Combining signals = robust detection
        
        Args:
            predictions: Model predictions
            labels: Ground truth labels
            probabilities: Prediction probabilities (optional)
            
        Returns:
            Tuple of (is_drift_detected, drift_report)
        """
        logger.info("Checking for model drift...")
        
        drift_signals = {}
        
        # Signal 1: Accuracy drop
        # WHY CHECK ACCURACY:
        # Most direct measure of performance
        # Clear indicator of problems
        current_accuracy = (predictions == labels).mean()
        baseline_accuracy = self.baseline_metrics.get('accuracy', 0.0)
        accuracy_drop = baseline_accuracy - current_accuracy
        
        drift_signals['accuracy_drop'] = {
            'baseline': baseline_accuracy,
            'current': current_accuracy,
            'drop': accuracy_drop,
            'is_drift': accuracy_drop > self.threshold
        }
        
        # Signal 2: Prediction distribution shift
        # WHY CHECK DISTRIBUTION:
        # Catches bias changes
        # E.g., model predicting "fracture" too often
        current_dist = self._get_prediction_distribution(predictions)
        baseline_dist = self.baseline_metrics.get('prediction_distribution', {})
        
        if baseline_dist:
            dist_shift = self._calculate_distribution_shift(
                baseline_dist, current_dist
            )
            drift_signals['distribution_shift'] = {
                'baseline': baseline_dist,
                'current': current_dist,
                'shift': dist_shift,
                'is_drift': dist_shift > 0.1  # WHY 0.1: 10% shift threshold
            }
        
        # Signal 3: Confidence degradation
        # WHY CHECK CONFIDENCE:
        # Model becoming uncertain
        # May indicate new data types
        if probabilities is not None:
            avg_confidence = np.max(probabilities, axis=1).mean()
            baseline_confidence = self.baseline_metrics.get('avg_confidence', 0.0)
            confidence_drop = baseline_confidence - avg_confidence
            
            drift_signals['confidence_drop'] = {
                'baseline': baseline_confidence,
                'current': avg_confidence,
                'drop': confidence_drop,
                'is_drift': confidence_drop > 0.1  # WHY 0.1: 10% drop threshold
            }
        
        # Signal 4: Statistical test
        # WHY STATISTICAL TEST:
        # Determines if difference is significant
        # Not just random variation
        if len(predictions) > 30:  # WHY 30: Minimum for statistical power
            stat_test = self._statistical_significance_test(
                predictions, labels
            )
            drift_signals['statistical_test'] = stat_test
        
        # Determine overall drift
        # WHY ANY SIGNAL:
        # Conservative approach for medical AI
        # Better to investigate false positive than miss real drift
        is_drift = any(
            signal.get('is_drift', False)
            for signal in drift_signals.values()
        )
        
        report = {
            'is_drift': is_drift,
            'signals': drift_signals,
            'recommendation': self._get_recommendation(drift_signals)
        }
        
        if is_drift:
            logger.warning(f"⚠ Model drift detected!")
            logger.warning(f"Recommendation: {report['recommendation']}")
        else:
            logger.info("✓ No drift detected")
        
        return is_drift, report
    
    def _get_prediction_distribution(
        self,
        predictions: np.ndarray
    ) -> Dict[int, float]:
        """
        Calculate prediction distribution
        
        WHY DISTRIBUTION:
            Shows class balance
            Detects bias
            E.g., {"no_fracture": 0.7, "fracture": 0.3}
        
        Args:
            predictions: Predicted labels
            
        Returns:
            Distribution dictionary
        """
        unique, counts = np.unique(predictions, return_counts=True)
        total = len(predictions)
        
        return {
            int(label): count / total
            for label, count in zip(unique, counts)
        }
    
    def _calculate_distribution_shift(
        self,
        baseline_dist: Dict,
        current_dist: Dict
    ) -> float:
        """
        Calculate distribution shift
        
        WHY KL DIVERGENCE:
            Measures difference between distributions
            Higher = more different
            Standard metric for distribution comparison
        
        ALTERNATIVE: Total Variation Distance
        
        Args:
            baseline_dist: Baseline distribution
            current_dist: Current distribution
            
        Returns:
            Shift magnitude
        """
        # Use Total Variation Distance (simpler than KL)
        # WHY TVD:
        # Bounded [0, 1]
        # Easy to interpret
        # Symmetric
        
        all_labels = set(baseline_dist.keys()) | set(current_dist.keys())
        
        shift = 0.0
        for label in all_labels:
            baseline_prob = baseline_dist.get(label, 0.0)
            current_prob = current_dist.get(label, 0.0)
            shift += abs(baseline_prob - current_prob)
        
        return shift / 2  # WHY /2: TVD normalization
    
    def _statistical_significance_test(
        self,
        predictions: np.ndarray,
        labels: np.ndarray
    ) -> Dict:
        """
        Perform statistical significance test
        
        WHY CHI-SQUARE:
            Tests if prediction distribution differs from expected
            Standard test for categorical data
            Provides p-value for significance
        
        Args:
            predictions: Model predictions
            labels: Ground truth
            
        Returns:
            Test results
        """
        # Create confusion matrix
        from sklearn.metrics import confusion_matrix
        
        cm = confusion_matrix(labels, predictions)
        
        # Chi-square test
        # WHY CHI-SQUARE:
        # Tests independence
        # Null hypothesis: predictions match labels
        # Low p-value = significant drift
        chi2, p_value = stats.chi2_contingency(cm)[:2]
        
        return {
            'test': 'chi_square',
            'statistic': float(chi2),
            'p_value': float(p_value),
            'is_drift': p_value < 0.05  # WHY 0.05: Standard significance level
        }
    
    def _get_recommendation(self, drift_signals: Dict) -> str:
        """
        Get actionable recommendation
        
        WHY RECOMMENDATIONS:
            Drift detection without action is useless
            Guide operators on next steps
            Automate response when possible
        
        Args:
            drift_signals: Detected drift signals
            
        Returns:
            Recommendation string
        """
        if drift_signals.get('accuracy_drop', {}).get('is_drift'):
            return (
                "CRITICAL: Accuracy dropped significantly. "
                "Retrain model immediately with recent data."
            )
        
        if drift_signals.get('confidence_drop', {}).get('is_drift'):
            return (
                "WARNING: Model confidence decreased. "
                "Investigate data distribution changes. "
                "Consider retraining."
            )
        
        if drift_signals.get('distribution_shift', {}).get('is_drift'):
            return (
                "NOTICE: Prediction distribution shifted. "
                "Monitor closely. May need retraining soon."
            )
        
        return "No action needed. Continue monitoring."


__all__ = ['ModelDriftDetector']
