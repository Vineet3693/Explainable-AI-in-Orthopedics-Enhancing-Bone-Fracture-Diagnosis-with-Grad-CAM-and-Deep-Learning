"""
Error Logger for Error Tracking and Analysis

PURPOSE:
    Logs all errors with stack traces and context for debugging.
    Helps identify and fix production issues quickly.

WHY ERROR LOGGING:
    Track errors, debug issues, prevent recurrence
    
    IMPACT: Faster bug fixes, better reliability

USAGE:
    from src.monitoring.logging.error_logger import ErrorLogger
    
    logger = ErrorLogger()
    try:
        risky_operation()
    except Exception as e:
        logger.log_error(e, context={'operation': 'prediction'})
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class ErrorLogger:
    """Error tracking logger"""
    
    def __init__(self, log_dir: str = 'logs/errors'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = 'error'
    ):
        """
        Log error with full context
        
        WHY LOG ERRORS:
            - Debug production issues
            - Track error patterns
            - Prevent recurrence
            - Monitor system health
        
        Args:
            error: Exception object
            context: Additional context
            severity: Error severity (error, critical)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            'severity': severity,
            'context': context or {}
        }
        
        # Write to daily log file
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.log_dir, f'errors_{date_str}.jsonl')
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.error(
            f"{type(error).__name__}: {str(error)}",
            exc_info=True
        )


__all__ = ['ErrorLogger']
