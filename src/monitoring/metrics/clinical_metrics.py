"""
Clinical Metrics for Medical AI Performance

PURPOSE:
    Tracks medical AI-specific metrics critical for patient safety.
    Monitors sensitivity, specificity, and false negative rate.

WHY CLINICAL METRICS:
    Standard ML metrics insufficient for medical AI
    Need to track patient safety metrics
    
    IMPACT: Ensure AI meets medical safety standards

KEY METRICS:
    - predictions_total: Total predictions by class
    - false_negatives_total: Missed fractures (CRITICAL)
    - false_positives_total: False alarms
    - sensitivity: True positive rate
    - specificity: True negative rate

MEDICAL AI REQUIREMENTS:
    - Sensitivity (Recall) > 95% (catch fractures)
    - False Negative Rate < 5% (patient safety)
    - Specificity > 90% (reduce false alarms)

USAGE:
    from src.monitoring.metrics.clinical_metrics import ClinicalMetrics
    
    metrics = ClinicalMetrics()
    metrics.record_prediction(
        predicted='fracture',
        actual='fracture',
        confidence=0.95
    )
"""

from prometheus_client import Counter, Gauge, Histogram
import logging

logger = logging.getLogger(__name__)


class ClinicalMetrics:
    """Medical AI clinical performance metrics"""
    
    def __init__(self):
        # WHY TRACK BY CLASS:
        # Need separate metrics for fracture vs normal
        self.predictions_total = Counter(
            'predictions_total',
            'Total predictions',
            ['predicted_class', 'actual_class']
        )
        
        # WHY SEPARATE FALSE NEGATIVE COUNTER:
        # Most critical metric for patient safety
        # Missed fractures can lead to serious complications
        self.false_negatives_total = Counter(
            'false_negatives_total',
            'Total false negatives (missed fractures)',
            ['anatomy']
        )
        
        self.false_positives_total = Counter(
            'false_positives_total',
            'Total false positives',
            ['anatomy']
        )
        
        # WHY GAUGE for rates:
        # Shows current performance, can go up or down
        self.sensitivity = Gauge(
            'model_sensitivity',
            'Current model sensitivity (recall)'
        )
        
        self.specificity = Gauge(
            'model_specificity',
            'Current model specificity'
        )
        
        self.confidence_scores = Histogram(
            'prediction_confidence_scores',
            'Prediction confidence distribution',
            ['predicted_class']
        )
    
    def record_prediction(
        self,
        predicted: str,
        actual: str,
        confidence: float,
        anatomy: str = 'unknown'
    ):
        """
        Record clinical prediction
        
        WHY TRACK ACTUAL vs PREDICTED:
            Need ground truth to calculate accuracy metrics
            In production, actual may come from radiologist review
        
        Args:
            predicted: AI prediction (fracture/normal)
            actual: Ground truth label
            confidence: Prediction confidence (0-1)
            anatomy: Anatomical location
        """
        # Record prediction
        self.predictions_total.labels(
            predicted_class=predicted,
            actual_class=actual
        ).inc()
        
        # Record confidence
        self.confidence_scores.labels(
            predicted_class=predicted
        ).observe(confidence)
        
        # WHY CHECK FOR FALSE NEGATIVES:
        # Most critical error type in medical AI
        # Missing a fracture can delay treatment
        if actual == 'fracture' and predicted == 'normal':
            self.false_negatives_total.labels(anatomy=anatomy).inc()
            logger.warning(
                f"FALSE NEGATIVE detected: {anatomy} fracture missed "
                f"(confidence: {confidence:.2f})"
            )
        
        # Track false positives
        if actual == 'normal' and predicted == 'fracture':
            self.false_positives_total.labels(anatomy=anatomy).inc()


__all__ = ['ClinicalMetrics']
