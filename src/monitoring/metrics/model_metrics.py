"""
Model performance metrics collection for Prometheus

PURPOSE:
    Collects and exposes CNN model performance metrics for Prometheus monitoring.
    Tracks prediction counts, inference times, confidence scores, and error rates.

METRICS TRACKED:
    - Prediction count (total, by class)
    - Inference time (mean, p50, p95, p99)
    - Confidence scores (distribution)
    - Error rate (validation failures, model errors)
    - Throughput (predictions per second)

WHY PROMETHEUS:
    - Industry standard for monitoring
    - Time-series database
    - Powerful querying (PromQL)
    - Grafana integration
    - Alerting capabilities

EXAMPLE USE:
    >>> from src.monitoring.metrics.model_metrics import ModelMetrics
    >>> metrics = ModelMetrics()
    >>> metrics.record_prediction(class_idx=1, confidence=0.95, inference_time=45)
"""

from prometheus_client import Counter, Histogram, Gauge
import logging

logger = logging.getLogger(__name__)

# Prediction counter
prediction_counter = Counter(
    'fracture_predictions_total',
    'Total number of predictions made',
    ['prediction_class']
)

# Inference time histogram
inference_time = Histogram(
    'fracture_inference_seconds',
    'Time spent on inference',
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0]
)

# Confidence score gauge
confidence_score = Gauge(
    'fracture_confidence_score',
    'Confidence score of predictions'
)

# Error counter
error_counter = Counter(
    'fracture_errors_total',
    'Total number of errors',
    ['error_type']
)


class ModelMetrics:
    """Collects model performance metrics"""
    
    def record_prediction(self, class_idx: int, confidence: float, inference_time_ms: float):
        """Record a prediction"""
        prediction_counter.labels(prediction_class=class_idx).inc()
        inference_time.observe(inference_time_ms / 1000)
        confidence_score.set(confidence)
    
    def record_error(self, error_type: str):
        """Record an error"""
        error_counter.labels(error_type=error_type).inc()
