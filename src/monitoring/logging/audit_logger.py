"""
Audit Logger for HIPAA Compliance

PURPOSE:
    HIPAA-compliant audit logging for PHI access and system events.
    Required for healthcare compliance and security audits.

WHY AUDIT LOGGING:
    HIPAA compliance, security audits, access tracking
    
    IMPACT: Regulatory compliance, security

USAGE:
    from src.monitoring.logging.audit_logger import AuditLogger
    
    logger = AuditLogger()
    logger.log_phi_access(user_id='doc123', patient_id='pat456', action='view')
"""

import json
import logging
from datetime import datetime
from typing import Optional
import os

logger = logging.getLogger(__name__)


class AuditLogger:
    """HIPAA-compliant audit logger"""
    
    def __init__(self, log_dir: str = 'logs/audit'):
        """
        Initialize audit logger
        
        WHY SEPARATE AUDIT LOGS:
            HIPAA requires 7-year retention
            Must be tamper-proof
            Separate from application logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_phi_access(
        self,
        user_id: str,
        patient_id: str,
        action: str,
        resource: Optional[str] = None,
        success: bool = True
    ):
        """
        Log PHI access event
        
        WHY LOG PHI ACCESS:
            HIPAA requires tracking all PHI access
            Detect unauthorized access
            Audit trail for investigations
        
        Args:
            user_id: User accessing PHI
            patient_id: Patient whose PHI was accessed
            action: Action performed (view, edit, delete)
            resource: Resource accessed
            success: Whether access succeeded
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'phi_access',
            'user_id': user_id,
            'patient_id': patient_id,
            'action': action,
            'resource': resource,
            'success': success
        }
        
        # WHY APPEND-ONLY:
        # Audit logs must be tamper-proof
        # Never delete or modify
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.log_dir, f'phi_access_{date_str}.jsonl')
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"PHI access: {user_id} {action} {patient_id}")


__all__ = ['AuditLogger']
