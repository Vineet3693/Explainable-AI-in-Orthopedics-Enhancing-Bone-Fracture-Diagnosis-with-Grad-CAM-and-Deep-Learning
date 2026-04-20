"""
Metrics Registry for Prometheus

PURPOSE:
    Central registry for all Prometheus metrics.
    Ensures consistent metric naming and prevents duplicates.

USAGE:
    from src.monitoring.core.metrics_registry import MetricsRegistry
    
    registry = MetricsRegistry()
    counter = registry.get_counter('predictions_total')
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
import logging

logger = logging.getLogger(__name__)


class MetricsRegistry:
    """Central registry for Prometheus metrics"""
    
    def __init__(self):
        self._metrics = {}
    
    def get_counter(self, name: str, description: str = "", labels: list = None):
        """Get or create a Counter metric"""
        if name not in self._metrics:
            self._metrics[name] = Counter(name, description, labels or [])
        return self._metrics[name]
    
    def get_histogram(self, name: str, description: str = "", labels: list = None):
        """Get or create a Histogram metric"""
        if name not in self._metrics:
            self._metrics[name] = Histogram(name, description, labels or [])
        return self._metrics[name]
    
    def get_gauge(self, name: str, description: str = "", labels: list = None):
        """Get or create a Gauge metric"""
        if name not in self._metrics:
            self._metrics[name] = Gauge(name, description, labels or [])
        return self._metrics[name]


__all__ = ['MetricsRegistry']
