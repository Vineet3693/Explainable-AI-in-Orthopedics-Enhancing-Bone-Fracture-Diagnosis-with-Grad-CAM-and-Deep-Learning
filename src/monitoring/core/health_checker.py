"""
Health Checker for System Health Monitoring

PURPOSE:
    Monitors system health and component availability.
    Provides health check endpoints for deployment.

USAGE:
    from src.monitoring.core.health_checker import HealthChecker
    
    checker = HealthChecker()
    health = checker.check_health()
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_function):
        """Register a health check"""
        self.checks[name] = check_function
    
    def check_health(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        for name, check_fn in self.checks.items():
            try:
                result = check_fn()
                results['checks'][name] = {
                    'status': 'pass' if result else 'fail',
                    'details': result
                }
                if not result:
                    results['status'] = 'unhealthy'
            except Exception as e:
                results['checks'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
                results['status'] = 'unhealthy'
        
        return results


__all__ = ['HealthChecker']
