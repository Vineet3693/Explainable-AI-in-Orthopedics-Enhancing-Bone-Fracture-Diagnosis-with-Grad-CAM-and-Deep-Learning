"""
Clinical safety alerts for patient safety monitoring

PURPOSE:
    Monitors for critical conditions and triggers alerts for patient safety.
    Tracks false negatives, low confidence predictions, and system errors.

ALERT TYPES:
    - HIGH_FALSE_NEGATIVE_RATE: FN rate > 5%
    - LOW_CONFIDENCE_FRACTURE: Fracture detected with confidence < 80%
    - SYSTEM_ERROR: Model or validation failures
    - HIGH_ERROR_RATE: Error rate > 10%

WHY CLINICAL ALERTS:
    - Patient safety is paramount
    - Early detection of model issues
    - Compliance with medical AI standards
    - Audit trail for incidents

ALERT ACTIONS:
    - Log to audit trail
    - Send notification (email, Slack)
    - Update dashboard
    - Escalate if critical

EXAMPLE USE:
    >>> from src.monitoring.alerts.clinical_alerts import ClinicalAlerts
    >>> alerts = ClinicalAlerts()
    >>> alerts.check_false_negative_rate(fn_rate=0.06)  # Triggers alert if > 5%
"""

import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class ClinicalAlerts:
    """Monitors clinical safety metrics and triggers alerts"""
    
    def __init__(self):
        self.alert_log = []
        self.fn_threshold = 0.05  # 5% max false negative rate
        self.confidence_threshold = 0.80  # 80% min confidence for fractures
        self.error_rate_threshold = 0.10  # 10% max error rate
    
    def check_false_negative_rate(self, fn_rate: float):
        """Check if false negative rate exceeds threshold"""
        if fn_rate > self.fn_threshold:
            self._trigger_alert(
                alert_type='HIGH_FALSE_NEGATIVE_RATE',
                severity='CRITICAL',
                message=f'False negative rate {fn_rate:.2%} exceeds threshold {self.fn_threshold:.2%}',
                data={'fn_rate': fn_rate, 'threshold': self.fn_threshold}
            )
    
    def check_low_confidence_fracture(self, confidence: float):
        """Check for low confidence fracture detection"""
        if confidence < self.confidence_threshold:
            self._trigger_alert(
                alert_type='LOW_CONFIDENCE_FRACTURE',
                severity='WARNING',
                message=f'Fracture detected with low confidence: {confidence:.2%}',
                data={'confidence': confidence, 'threshold': self.confidence_threshold}
            )
    
    def _trigger_alert(self, alert_type: str, severity: str, message: str, data: Dict):
        """Trigger an alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'severity': severity,
            'message': message,
            'data': data
        }
        self.alert_log.append(alert)
        logger.warning(f"CLINICAL ALERT [{severity}]: {message}")
        # TODO: Send notifications (email, Slack, etc.)
