"""
Monitoring Alerts subpackage for clinical safety monitoring

PACKAGE PURPOSE:
    Contains modules for monitoring clinical safety metrics and triggering
    alerts when critical thresholds are exceeded.

MODULES:
    - clinical_alerts.py: Patient safety alert system

ALERT TYPES:
    - HIGH_FALSE_NEGATIVE_RATE: FN rate > 5% (CRITICAL)
    - LOW_CONFIDENCE_FRACTURE: Fracture detected with confidence < 80% (WARNING)
    - SYSTEM_ERROR: Model or validation failures (ERROR)
    - HIGH_ERROR_RATE: Error rate > 10% (WARNING)

ALERT SEVERITY LEVELS:
    - CRITICAL: Immediate action required (patient safety risk)
    - WARNING: Attention needed (potential issue)
    - INFO: Informational (no action needed)

ALERT ACTIONS:
    1. Log to audit trail
    2. Send notification (email, Slack, PagerDuty)
    3. Update monitoring dashboard
    4. Escalate if critical

USAGE:
    from src.monitoring.alerts import ClinicalAlerts
    
    alerts = ClinicalAlerts()
    alerts.check_false_negative_rate(fn_rate=0.06)  # Triggers if >5%
"""

__all__ = [
    'ClinicalAlerts'
]
