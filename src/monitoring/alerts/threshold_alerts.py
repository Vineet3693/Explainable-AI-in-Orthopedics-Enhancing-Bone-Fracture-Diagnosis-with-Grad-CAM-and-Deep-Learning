"""
Threshold Alerts for Metric-Based Alerting

PURPOSE:
    Triggers alerts when metrics exceed defined thresholds.
    Essential for proactive monitoring and incident prevention.

WHY THRESHOLD ALERTS:
    Detect issues before they impact users
    
    IMPACT: Proactive incident prevention

USAGE:
    from src.monitoring.alerts.threshold_alerts import ThresholdAlerts
    
    alerts = ThresholdAlerts()
    alerts.check_threshold('false_negative_rate', 0.06, max_value=0.05)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ThresholdAlerts:
    """Threshold-based alerting"""
    
    def __init__(self, alert_manager=None):
        self.alert_manager = alert_manager
        self.thresholds = self._default_thresholds()
    
    def _default_thresholds(self):
        """
        Default thresholds for medical AI
        
        WHY THESE THRESHOLDS:
            - False Negative Rate < 5%: Patient safety
            - API Latency < 3s: User experience
            - Error Rate < 1%: Reliability
            - Cost per diagnosis < $0.10: Budget
        """
        return {
            'false_negative_rate': {'max': 0.05, 'severity': 'critical'},
            'api_latency_p95': {'max': 3.0, 'severity': 'warning'},
            'error_rate': {'max': 0.01, 'severity': 'warning'},
            'cost_per_diagnosis': {'max': 0.10, 'severity': 'warning'},
            'daily_active_users': {'min': 10, 'severity': 'info'}
        }
    
    def check_threshold(
        self,
        metric_name: str,
        value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ):
        """
        Check if metric exceeds threshold
        
        Args:
            metric_name: Metric name
            value: Current value
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value
        """
        threshold = self.thresholds.get(metric_name, {})
        
        # Check max threshold
        if max_value or 'max' in threshold:
            limit = max_value or threshold['max']
            if value > limit:
                self._trigger_alert(
                    metric_name,
                    value,
                    limit,
                    'exceeded',
                    threshold.get('severity', 'warning')
                )
        
        # Check min threshold
        if min_value or 'min' in threshold:
            limit = min_value or threshold['min']
            if value < limit:
                self._trigger_alert(
                    metric_name,
                    value,
                    limit,
                    'below',
                    threshold.get('severity', 'warning')
                )
    
    def _trigger_alert(
        self,
        metric_name: str,
        value: float,
        threshold: float,
        condition: str,
        severity: str
    ):
        """Trigger threshold alert"""
        message = f"{metric_name} is {condition} threshold: {value:.4f} (threshold: {threshold:.4f})"
        
        if self.alert_manager:
            self.alert_manager.send_alert(
                title=f"Threshold Alert: {metric_name}",
                severity=severity,
                message=message,
                tags={'metric': metric_name, 'type': 'threshold'}
            )
        else:
            logger.warning(f"THRESHOLD ALERT [{severity.upper()}]: {message}")


__all__ = ['ThresholdAlerts']
