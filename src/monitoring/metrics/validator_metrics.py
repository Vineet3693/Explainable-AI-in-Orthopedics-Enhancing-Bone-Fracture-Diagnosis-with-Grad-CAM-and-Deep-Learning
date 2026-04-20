"""
Validator Metrics for Validation Pipeline Monitoring

PURPOSE:
    Tracks validation pipeline performance and rejection rates.
    Helps optimize validation thresholds and identify issues.

WHY VALIDATOR METRICS:
    Track rejection rates, identify problematic images, optimize thresholds
    
    IMPACT: Better validation accuracy, fewer false rejections

KEY METRICS:
    - validation_checks_total: Total validation checks
    - validation_rejections_total: Rejections by stage
    - validation_duration_seconds: Validation time
    - validation_quality_scores: Image quality distribution

USAGE:
    from src.monitoring.metrics.validator_metrics import ValidatorMetrics
    
    metrics = ValidatorMetrics()
    metrics.record_validation('format', passed=True, duration=0.005)
"""

from prometheus_client import Counter, Histogram, Summary
import logging

logger = logging.getLogger(__name__)


class ValidatorMetrics:
    """Validation pipeline metrics"""
    
    def __init__(self):
        self.checks_total = Counter(
            'validation_checks_total',
            'Total validation checks',
            ['stage', 'result']
        )
        
        self.rejections_total = Counter(
            'validation_rejections_total',
            'Total rejections by stage',
            ['stage', 'reason']
        )
        
        self.duration_seconds = Histogram(
            'validation_duration_seconds',
            'Validation duration by stage',
            ['stage']
        )
        
        self.quality_scores = Summary(
            'validation_quality_scores',
            'Image quality score distribution'
        )
    
    def record_validation(
        self,
        stage: str,
        passed: bool,
        duration: float,
        reason: str = None,
        quality_score: float = None
    ):
        """
        Record validation result
        
        Args:
            stage: Validation stage (format, xray, anatomy, quality)
            passed: Whether validation passed
            duration: Validation duration in seconds
            reason: Rejection reason if failed
            quality_score: Quality score if applicable
        """
        # Record check
        result = 'pass' if passed else 'fail'
        self.checks_total.labels(stage=stage, result=result).inc()
        
        # Record rejection
        if not passed and reason:
            self.rejections_total.labels(stage=stage, reason=reason).inc()
        
        # Record duration
        self.duration_seconds.labels(stage=stage).observe(duration)
        
        # Record quality score
        if quality_score is not None:
            self.quality_scores.observe(quality_score)


__all__ = ['ValidatorMetrics']
