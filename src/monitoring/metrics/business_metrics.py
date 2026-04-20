"""
Business Metrics for KPI Tracking

PURPOSE:
    Tracks business KPIs like user engagement, satisfaction, and retention.

KEY METRICS:
    - daily_active_users: DAU
    - diagnoses_per_day: Daily throughput
    - user_satisfaction_score: Average rating
    - radiologist_agreement_rate: AI vs radiologist agreement

USAGE:
    from src.monitoring.metrics.business_metrics import BusinessMetrics
    
    metrics = BusinessMetrics()
    metrics.record_user_activity(user_id='user123')
"""

from prometheus_client import Counter, Gauge, Histogram
import logging

logger = logging.getLogger(__name__)


class BusinessMetrics:
    """Business KPI metrics"""
    
    def __init__(self):
        self.active_users = Gauge(
            'daily_active_users',
            'Daily active users'
        )
        
        self.diagnoses_total = Counter(
            'diagnoses_total',
            'Total diagnoses performed'
        )
        
        self.user_satisfaction = Histogram(
            'user_satisfaction_score',
            'User satisfaction ratings'
        )
        
        self.radiologist_agreement = Gauge(
            'radiologist_agreement_rate',
            'AI-radiologist agreement rate'
        )
    
    def record_diagnosis(self):
        """Record a diagnosis"""
        self.diagnoses_total.inc()
    
    def record_satisfaction(self, score: float):
        """Record user satisfaction (1-5)"""
        self.user_satisfaction.observe(score)


__all__ = ['BusinessMetrics']
