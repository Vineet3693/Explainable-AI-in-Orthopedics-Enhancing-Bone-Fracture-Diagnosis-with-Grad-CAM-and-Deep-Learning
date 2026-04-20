"""
Monitoring Logging subpackage for HIPAA-compliant structured logging

PACKAGE PURPOSE:
    Contains modules for structured JSON logging with HIPAA compliance
    for audit trails and regulatory requirements.

MODULES:
    - structured_logger.py: HIPAA-compliant structured logger

KEY CONCEPTS:
    - Structured Logging: JSON format for easy parsing and analysis
    - HIPAA Compliance: Healthcare data privacy regulations
    - Audit Trail: Log of all data access and predictions (7-year retention)
    - PHI: Protected Health Information (must be anonymized in logs)
    - Log Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

LOGGED EVENTS:
    - Data Access: Who accessed what data, when
    - Predictions: Image ID, prediction, confidence, timestamp
    - System Events: Errors, warnings, configuration changes
    - User Actions: Login, logout, settings changes

HIPAA REQUIREMENTS:
    - All data access must be logged
    - PHI must be anonymized (hashed identifiers)
    - 7-year retention period
    - Audit trail for compliance

USAGE:
    from src.monitoring.logging import get_logger
    
    logger = get_logger(__name__)
    logger.log_prediction(image_id='12345', prediction='fracture', confidence=0.95)
"""

__all__ = [
    'StructuredLogger',
    'get_logger'
]
