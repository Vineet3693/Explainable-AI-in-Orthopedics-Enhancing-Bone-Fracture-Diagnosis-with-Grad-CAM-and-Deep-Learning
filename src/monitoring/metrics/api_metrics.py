"""
API Metrics for Monitoring API Performance

PURPOSE:
    Tracks API endpoint performance including latency, throughput, and errors.
    Essential for monitoring production API health.

WHY API METRICS:
    No metrics: Can't detect performance issues
    Basic logging: Hard to analyze trends
    Prometheus metrics (this): Real-time monitoring, alerting
    
    IMPACT: Detect issues before users complain

DESIGN PHILOSOPHY:
    1. Track all endpoints
    2. Measure latency (p50, p95, p99)
    3. Count errors by type
    4. Monitor throughput (requests/sec)

KEY METRICS:
    - api_requests_total: Total API requests
    - api_request_duration_seconds: Request latency
    - api_errors_total: Error count by type
    - api_active_requests: Current active requests

PROS:
    ✅ Real-time monitoring
    ✅ Historical trends
    ✅ Alerting on thresholds
    ✅ Performance optimization data

CONS:
    ❌ Storage overhead
    ❌ Slight performance impact
    ❌ Requires Prometheus setup

USAGE:
    from src.monitoring.metrics.api_metrics import APIMetrics
    
    metrics = APIMetrics()
    
    # Track request
    with metrics.track_request('/predict'):
        result = predict_fracture(image)
"""

from prometheus_client import Counter, Histogram, Gauge
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class APIMetrics:
    """API performance metrics"""
    
    def __init__(self):
        # WHY COUNTER for requests:
        # Counts always increase, perfect for total requests
        self.requests_total = Counter(
            'api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status']
        )
        
        # WHY HISTOGRAM for latency:
        # Automatically calculates percentiles (p50, p95, p99)
        self.request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration',
            ['endpoint', 'method']
        )
        
        # WHY COUNTER for errors:
        # Track error trends over time
        self.errors_total = Counter(
            'api_errors_total',
            'Total API errors',
            ['endpoint', 'error_type']
        )
        
        # WHY GAUGE for active requests:
        # Shows current load, goes up and down
        self.active_requests = Gauge(
            'api_active_requests',
            'Currently active API requests',
            ['endpoint']
        )
    
    @contextmanager
    def track_request(self, endpoint: str, method: str = 'POST'):
        """
        Track API request metrics
        
        WHY CONTEXT MANAGER:
            Automatically tracks start/end
            Handles exceptions gracefully
            Ensures metrics always recorded
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            
        Usage:
            with metrics.track_request('/predict'):
                result = process_request()
        """
        # Increment active requests
        self.active_requests.labels(endpoint=endpoint).inc()
        
        start_time = time.time()
        status = 'success'
        
        try:
            yield
        except Exception as e:
            status = 'error'
            error_type = type(e).__name__
            self.errors_total.labels(
                endpoint=endpoint,
                error_type=error_type
            ).inc()
            raise
        finally:
            # Record duration
            duration = time.time() - start_time
            self.request_duration.labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
            
            # Record request
            self.requests_total.labels(
                endpoint=endpoint,
                method=method,
                status=status
            ).inc()
            
            # Decrement active requests
            self.active_requests.labels(endpoint=endpoint).dec()
            
            logger.debug(f"{endpoint} completed in {duration:.3f}s")


__all__ = ['APIMetrics']
