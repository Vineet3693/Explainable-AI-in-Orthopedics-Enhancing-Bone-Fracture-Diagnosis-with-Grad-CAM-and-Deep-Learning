"""
Structured Logger for HIPAA-Compliant Logging

PURPOSE:
    HIPAA-compliant structured logging with PHI anonymization.
    Logs in JSON format for easy parsing and analysis.

WHY STRUCTURED LOGGING:
    Text logs: Hard to parse, no structure
    Structured logs (JSON): Easy to query, analyze
    
    IMPACT: Better debugging, compliance, analytics

USAGE:
    from src.monitoring.logging.structured_logger import StructuredLogger
    
    logger = StructuredLogger('app')
    logger.log_event('prediction_made', {'result': 'fracture'})
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any
import hashlib


class StructuredLogger:
    """HIPAA-compliant structured logger"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        anonymize_phi: bool = True
    ):
        """
        Log structured event
        
        Args:
            event_type: Type of event
            data: Event data
            anonymize_phi: Whether to anonymize PHI
        """
        if anonymize_phi:
            data = self._anonymize_phi(data)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def _anonymize_phi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize PHI in data"""
        # Simple anonymization - hash sensitive fields
        sensitive_fields = ['patient_id', 'patient_name', 'mrn']
        
        anonymized = data.copy()
        for field in sensitive_fields:
            if field in anonymized:
                value = str(anonymized[field])
                anonymized[field] = hashlib.sha256(value.encode()).hexdigest()[:16]
        
        return anonymized


__all__ = ['StructuredLogger']
