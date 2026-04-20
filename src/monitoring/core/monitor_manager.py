"""
Monitoring Manager - Central Coordinator

PURPOSE:
    Central coordinator for all monitoring activities.
    Manages metrics collection, logging, and alerting.

WHY CENTRALIZED:
    Scattered monitoring: Hard to manage
    Central manager: Single point of control
    
    IMPACT: Easier monitoring management

USAGE:
    from src.monitoring.core.monitor_manager import MonitorManager
    
    manager = MonitorManager()
    manager.start()
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MonitorManager:
    """Central monitoring coordinator"""
    
    def __init__(self):
        self.metrics = {}
        self.is_running = False
    
    def start(self):
        """Start monitoring"""
        self.is_running = True
        logger.info("Monitoring started")
    
    def stop(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info("Monitoring stopped")
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'tags': tags or {},
            'timestamp': logging.time.time()
        })


__all__ = ['MonitorManager']
