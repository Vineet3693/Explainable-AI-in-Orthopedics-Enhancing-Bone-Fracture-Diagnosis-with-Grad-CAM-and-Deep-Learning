"""
Monitoring package for production system observability

PACKAGE PURPOSE:
    Contains modules for monitoring model performance, LLM usage, clinical
    safety, and system health in production. Integrates with Prometheus
    and Grafana for real-time dashboards.

SUBPACKAGES:
    - metrics/: Prometheus metrics collection
    - alerts/: Clinical safety alerts
    - logging/: Structured HIPAA-compliant logging
    - dashboards/: Grafana dashboard configurations
    - profilers/: Performance profiling
    - tracers/: Distributed tracing

KEY CONCEPTS:
    - Prometheus: Time-series metrics database
    - Grafana: Visualization and dashboarding
    - Metrics: Quantitative measurements (counters, gauges, histograms)
    - Alerts: Automated notifications for critical conditions
    - HIPAA Compliance: Healthcare data privacy regulations
    - Audit Trail: Log of all data access and predictions
    - SLO: Service Level Objective (target performance)
    - SLA: Service Level Agreement (guaranteed performance)

MONITORED METRICS:
    Model Performance:
        - Prediction count (total, by class)
        - Inference time (mean, p50, p95, p99)
        - Confidence scores (distribution)
        - Error rate (validation failures, model errors)
    
    LLM Usage:
        - API calls (by provider, operation)
        - Token usage (input, output, total)
        - Cost (per call, cumulative)
        - Response time (mean, p95)
    
    Clinical Safety:
        - False negative rate (must be <5%)
        - Low confidence fractures (confidence <80%)
        - System errors
        - High error rate (>10%)

USAGE:
    from src.monitoring.metrics import ModelMetrics, LLMMetrics
    from src.monitoring.alerts import ClinicalAlerts
    
    model_metrics = ModelMetrics()
    model_metrics.record_prediction(class_idx=1, confidence=0.95, time_ms=45)
    
    alerts = ClinicalAlerts()
    alerts.check_false_negative_rate(fn_rate=0.06)  # Triggers if >5%
"""

__all__ = [
    'ModelMetrics',
    'LLMMetrics',
    'ClinicalAlerts',
    'StructuredLogger'
]
