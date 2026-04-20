"""
Monitoring Metrics subpackage for Prometheus metrics collection

PACKAGE PURPOSE:
    Contains modules for collecting and exposing metrics to Prometheus
    for real-time monitoring and alerting.

MODULES:
    - model_metrics.py: CNN model performance metrics
    - llm_metrics.py: LLM usage and cost tracking

PROMETHEUS METRICS TYPES:
    - Counter: Monotonically increasing value (e.g., total predictions)
    - Gauge: Value that can go up or down (e.g., current confidence)
    - Histogram: Distribution of values (e.g., inference time buckets)
    - Summary: Similar to histogram but calculates quantiles

COLLECTED METRICS:
    Model:
        - fracture_predictions_total (counter)
        - fracture_inference_seconds (histogram)
        - fracture_confidence_score (gauge)
        - fracture_errors_total (counter)
    
    LLM:
        - llm_calls_total (counter)
        - llm_tokens_total (counter)
        - llm_cost_dollars_total (counter)
        - llm_response_seconds (histogram)

USAGE:
    from src.monitoring.metrics import ModelMetrics
    
    metrics = ModelMetrics()
    metrics.record_prediction(class_idx=1, confidence=0.95, time_ms=45)
"""

__all__ = [
    'ModelMetrics',
    'LLMMetrics'
]
