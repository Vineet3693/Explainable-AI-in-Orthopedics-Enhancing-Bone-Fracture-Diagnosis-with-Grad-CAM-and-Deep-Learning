"""
Alert Manager for Centralized Alert Management

PURPOSE:
    Central manager for all system alerts and notifications.
    Coordinates alert generation, routing, and delivery.

WHY ALERT MANAGER:
    Centralized alert management, consistent routing, easy configuration
    
    IMPACT: Faster incident response, better reliability

KEY FEATURES:
    - Alert prioritization (critical, warning, info)
    - Multi-channel notifications (email, slack, pagerduty)
    - Alert deduplication
    - Alert history tracking

USAGE:
    from src.monitoring.alerts.alert_manager import AlertManager
    
    manager = AlertManager()
    manager.send_alert(
        title='High False Negative Rate',
        severity='critical',
        message='FN rate exceeded 5%'
    )
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


class AlertManager:
    """Central alert management system"""
    
    def __init__(self, alerts_dir: str = 'alerts'):
        """
        Initialize alert manager
        
        WHY TRACK ALERTS:
            - Monitor alert frequency
            - Prevent alert fatigue
            - Audit trail
            - Analyze patterns
        
        Args:
            alerts_dir: Directory for alert history
        """
        self.alerts_dir = alerts_dir
        os.makedirs(alerts_dir, exist_ok=True)
        self.active_alerts = []
        self.alert_history = []
    
    def send_alert(
        self,
        title: str,
        severity: str,
        message: str,
        tags: Optional[Dict[str, str]] = None,
        channels: Optional[List[str]] = None
    ):
        """
        Send alert
        
        WHY SEVERITY LEVELS:
            - Critical: Immediate action required (page on-call)
            - Warning: Investigate soon (email)
            - Info: FYI only (log only)
        
        Args:
            title: Alert title
            severity: Severity level (critical, warning, info)
            message: Alert message
            tags: Alert tags for categorization
            channels: Notification channels (email, slack, pagerduty)
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'severity': severity,
            'message': message,
            'tags': tags or {},
            'channels': channels or self._default_channels(severity),
            'status': 'active'
        }
        
        # WHY CHECK FOR DUPLICATES:
        # Prevent alert fatigue from repeated alerts
        # Only send if not already active
        if not self._is_duplicate(alert):
            self.active_alerts.append(alert)
            self._deliver_alert(alert)
            self._save_alert(alert)
            
            logger.warning(f"ALERT [{severity.upper()}]: {title} - {message}")
        else:
            logger.debug(f"Duplicate alert suppressed: {title}")
    
    def _default_channels(self, severity: str) -> List[str]:
        """Get default notification channels for severity"""
        if severity == 'critical':
            return ['pagerduty', 'slack', 'email']
        elif severity == 'warning':
            return ['slack', 'email']
        else:  # info
            return ['log']
    
    def _is_duplicate(self, alert: Dict[str, Any]) -> bool:
        """Check if alert is duplicate of active alert"""
        for active in self.active_alerts:
            if (active['title'] == alert['title'] and 
                active['severity'] == alert['severity'] and
                active['status'] == 'active'):
                return True
        return False
    
    def _deliver_alert(self, alert: Dict[str, Any]):
        """Deliver alert to configured channels"""
        for channel in alert['channels']:
            if channel == 'log':
                logger.warning(f"Alert: {alert['title']}")
            elif channel == 'email':
                self._send_email(alert)
            elif channel == 'slack':
                self._send_slack(alert)
            elif channel == 'pagerduty':
                self._send_pagerduty(alert)
    
    def _send_email(self, alert: Dict[str, Any]):
        """Send email notification"""
        # Placeholder - implement actual email sending
        logger.info(f"Would send email for: {alert['title']}")
    
    def _send_slack(self, alert: Dict[str, Any]):
        """Send Slack notification"""
        # Placeholder - implement actual Slack integration
        logger.info(f"Would send Slack message for: {alert['title']}")
    
    def _send_pagerduty(self, alert: Dict[str, Any]):
        """Send PagerDuty alert"""
        # Placeholder - implement actual PagerDuty integration
        logger.info(f"Would page on-call for: {alert['title']}")
    
    def _save_alert(self, alert: Dict[str, Any]):
        """Save alert to history"""
        date_str = datetime.now().strftime('%Y%m%d')
        alert_file = os.path.join(self.alerts_dir, f'alerts_{date_str}.jsonl')
        
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
    
    def resolve_alert(self, title: str):
        """Mark alert as resolved"""
        for alert in self.active_alerts:
            if alert['title'] == title and alert['status'] == 'active':
                alert['status'] = 'resolved'
                alert['resolved_at'] = datetime.now().isoformat()
                logger.info(f"Alert resolved: {title}")


__all__ = ['AlertManager']
