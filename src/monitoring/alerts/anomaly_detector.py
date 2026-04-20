"""
Anomaly Detector for ML-Based Anomaly Detection

PURPOSE:
    Uses statistical methods to detect anomalies in metrics.
    Complements threshold alerts with adaptive detection.

WHY ANOMALY DETECTION:
    Detect unusual patterns that thresholds miss
    
    IMPACT: Catch subtle issues early

USAGE:
    from src.monitoring.alerts.anomaly_detector import AnomalyDetector
    
    detector = AnomalyDetector()
    is_anomaly = detector.detect_anomaly('api_latency', 5.2)
"""

import logging
import numpy as np
from collections import deque
from typing import Optional

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """ML-based anomaly detection"""
    
    def __init__(self, window_size: int = 100, std_threshold: float = 3.0):
        """
        Initialize anomaly detector
        
        WHY STATISTICAL APPROACH:
            - Simple and effective
            - No training data needed
            - Works well for time series
        
        Args:
            window_size: Number of recent values to track
            std_threshold: Number of standard deviations for anomaly
        """
        self.window_size = window_size
        self.std_threshold = std_threshold
        self.metric_windows = {}
    
    def detect_anomaly(
        self,
        metric_name: str,
        value: float,
        alert_manager=None
    ) -> bool:
        """
        Detect if value is anomalous
        
        WHY Z-SCORE METHOD:
            - Detects values far from mean
            - Adapts to changing patterns
            - Simple to understand
        
        Args:
            metric_name: Metric name
            value: Current value
            alert_manager: Alert manager for notifications
            
        Returns:
            True if anomalous
        """
        # Initialize window if needed
        if metric_name not in self.metric_windows:
            self.metric_windows[metric_name] = deque(maxlen=self.window_size)
        
        window = self.metric_windows[metric_name]
        
        # Need enough data for detection
        if len(window) < 10:
            window.append(value)
            return False
        
        # Calculate statistics
        mean = np.mean(window)
        std = np.std(window)
        
        # Calculate z-score
        if std > 0:
            z_score = abs((value - mean) / std)
        else:
            z_score = 0
        
        # Detect anomaly
        is_anomaly = z_score > self.std_threshold
        
        if is_anomaly:
            message = f"{metric_name} anomaly detected: {value:.4f} (mean: {mean:.4f}, std: {std:.4f}, z-score: {z_score:.2f})"
            
            if alert_manager:
                alert_manager.send_alert(
                    title=f"Anomaly Detected: {metric_name}",
                    severity='warning',
                    message=message,
                    tags={'metric': metric_name, 'type': 'anomaly'}
                )
            else:
                logger.warning(f"ANOMALY: {message}")
        
        # Add to window
        window.append(value)
        
        return is_anomaly


__all__ = ['AnomalyDetector']
