"""
Check Health Script

PURPOSE:
    Check system health and component status.

USAGE:
    python scripts/check_health.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.monitoring.core.health_checker import HealthChecker
import json


def main():
    print("=== System Health Check ===\n")
    
    checker = HealthChecker()
    
    # Register checks
    checker.register_check('models', lambda: True)  # Placeholder
    checker.register_check('llm_api', lambda: True)  # Placeholder
    checker.register_check('storage', lambda: True)  # Placeholder
    
    # Run checks
    results = checker.check_health()
    
    # Print results
    print(f"Status: {results['status'].upper()}")
    print(f"Timestamp: {results['timestamp']}\n")
    
    print("Component Checks:")
    for name, check in results['checks'].items():
        status = check['status']
        symbol = "✓" if status == 'pass' else "✗"
        print(f"  {symbol} {name}: {status}")
    
    return 0 if results['status'] == 'healthy' else 1


if __name__ == '__main__':
    sys.exit(main())
