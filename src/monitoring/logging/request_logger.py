"""
Request Logger for API Request Logging

PURPOSE:
    Logs all API requests with details for debugging and audit trails.
    Captures request/response data, timing, and errors.

WHY REQUEST LOGGING:
    Debug production issues, audit trail, performance analysis
    
    IMPACT: Faster debugging, compliance, analytics

USAGE:
    from src.monitoring.logging.request_logger import RequestLogger
    
    logger = RequestLogger()
    logger.log_request(endpoint='/predict', method='POST', status=200, duration=1.5)
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class RequestLogger:
    """API request logger"""
    
    def __init__(self, log_dir: str = 'logs/requests'):
        """
        Initialize request logger
        
        WHY SEPARATE LOG DIRECTORY:
            Keep request logs separate from application logs
            Easier to analyze, archive, and manage
        
        Args:
            log_dir: Directory for request logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_request(
        self,
        endpoint: str,
        method: str,
        status: int,
        duration: float,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Log API request
        
        WHY LOG ALL THIS DATA:
            - Endpoint/method: What was called
            - Status: Success or error
            - Duration: Performance tracking
            - Request/response: Debugging
            - Error: Troubleshooting
            - User: Usage analytics
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            status: HTTP status code
            duration: Request duration in seconds
            request_data: Request payload (optional)
            response_data: Response data (optional)
            error: Error message if failed
            user_id: User identifier
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'duration_seconds': duration,
            'user_id': user_id,
            'error': error
        }
        
        # WHY NOT LOG FULL REQUEST/RESPONSE:
        # Can contain PHI or large data
        # Only log if explicitly provided and sanitized
        if request_data:
            log_entry['request_summary'] = self._summarize_data(request_data)
        
        if response_data:
            log_entry['response_summary'] = self._summarize_data(response_data)
        
        # Write to daily log file
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.log_dir, f'requests_{date_str}.jsonl')
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Also log to standard logger
        logger.info(
            f"{method} {endpoint} - {status} - {duration:.3f}s"
            + (f" - Error: {error}" if error else "")
        )
    
    def _summarize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize data for logging
        
        WHY SUMMARIZE:
            Full data can be huge (images, etc.)
            Only log metadata, not actual content
        
        Args:
            data: Data to summarize
            
        Returns:
            Summarized data
        """
        summary = {}
        
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                if len(str(value)) < 100:  # Only short values
                    summary[key] = value
                else:
                    summary[key] = f"<{type(value).__name__} length={len(str(value))}>"
            else:
                summary[key] = f"<{type(value).__name__}>"
        
        return summary


__all__ = ['RequestLogger']
