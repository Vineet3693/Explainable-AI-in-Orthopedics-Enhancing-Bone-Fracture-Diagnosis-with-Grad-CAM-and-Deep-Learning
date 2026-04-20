"""
Data Drift Detector

PURPOSE:
    Detects changes in input data distribution over time.
    Monitors X-ray image characteristics and alerts on distribution shifts.

WHY DATA DRIFT DETECTION:
    Input data changes: New equipment, patient demographics, imaging protocols
    Data drift (this): Detect changes before they hurt performance
    
    IMPACT: Proactive model maintenance, sustained quality

DESIGN PHILOSOPHY:
    1. Multiple drift metrics (statistical, visual, metadata)
    2. Feature-based detection
    3. Configurable sensitivity
    4. Clear visualizations

PROS:
    ✅ Early warning system
    ✅ No labels needed
    ✅ Catches data quality issues
    ✅ Prevents model degradation

CONS:
    ❌ May have false positives
    ❌ Requires baseline data
    ❌ Computationally expensive

COMPARISON:
    | Method              | Sensitivity | Speed | Interpretability | Labels |
    |---------------------|-------------|-------|------------------|--------|
    | KS Test             | High        | Fast  | Medium           | No     |
    | Population Stability| Medium      | Fast  | High             | No     |
    | MMD                 | High        | Slow  | Low              | No     |
    | Adversarial         | High        | Medium| Low              | No     |

USAGE:
    from src.evaluation.data_drift_detector import DataDriftDetector
    
    detector = DataDriftDetector(baseline_data)
    
    # Check for drift
    is_drift, report = detector.detect_drift(new_data)
"""

import numpy as np
from typing import Dict, Tuple, List, Optional
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class DataDriftDetector:
    """Detects input data distribution drift"""
    
    def __init__(
        self,
        baseline_data: np.ndarray,
        threshold: float = 0.05
    ):
        """
        Initialize data drift detector
        
        WHY BASELINE:
            Reference distribution
            Typically from training/validation set
            Represents "normal" data
        
        WHY THRESHOLD:
            0.05 = 5% significance level
            Standard for statistical tests
            Lower = more sensitive
        
        Args:
            baseline_data: Reference data distribution
            threshold: Significance threshold for drift detection
        """
        self.baseline_data = baseline_data
        self.threshold = threshold
        
        # Calculate baseline statistics
        # WHY PRECOMPUTE:
        # Faster drift detection
        # Consistent reference
        self.baseline_stats = self._calculate_statistics(baseline_data)
        
        logger.info(
            f"Initialized DataDriftDetector "
            f"(baseline_size={len(baseline_data)}, threshold={threshold})"
        )
    
    def detect_drift(
        self,
        current_data: np.ndarray,
        features: Optional[List[str]] = None
    ) -> Tuple[bool, Dict]:
        """
        Detect data drift
        
        WHY MULTIPLE TESTS:
            Different tests catch different drift types
            Combining tests = robust detection
            Statistical rigor
        
        Args:
            current_data: Current data to check
            features: Feature names (optional, for reporting)
            
        Returns:
            Tuple of (is_drift_detected, drift_report)
        """
        logger.info(f"Checking for data drift on {len(current_data)} samples...")
        
        drift_signals = {}
        
        # Signal 1: Kolmogorov-Smirnov test
        # WHY KS TEST:
        # Tests if two samples from same distribution
        # Non-parametric (no assumptions about distribution)
        # Standard statistical test
        ks_results = self._ks_test(current_data)
        drift_signals['ks_test'] = ks_results
        
        # Signal 2: Population Stability Index
        # WHY PSI:
        # Industry standard for drift detection
        # Easy to interpret
        # Works well for binned data
        psi_results = self._population_stability_index(current_data)
        drift_signals['psi'] = psi_results
        
        # Signal 3: Statistical moments
        # WHY MOMENTS:
        # Mean shift = location change
        # Std shift = spread change
        # Skew/kurtosis = shape change
        moments_results = self._check_statistical_moments(current_data)
        drift_signals['moments'] = moments_results
        
        # Signal 4: Feature-wise drift
        # WHY FEATURE-WISE:
        # Identifies which features drifted
        # Actionable insights
        # Helps debug issues
        if len(current_data.shape) > 1:
            feature_results = self._check_feature_drift(current_data, features)
            drift_signals['features'] = feature_results
        
        # Determine overall drift
        # WHY ANY SIGNAL:
        # Conservative for medical AI
        # Better safe than sorry
        is_drift = any(
            signal.get('is_drift', False)
            for signal in drift_signals.values()
        )
        
        report = {
            'is_drift': is_drift,
            'signals': drift_signals,
            'severity': self._calculate_severity(drift_signals),
            'recommendation': self._get_recommendation(drift_signals)
        }
        
        if is_drift:
            logger.warning(f"⚠ Data drift detected!")
            logger.warning(f"Severity: {report['severity']}")
            logger.warning(f"Recommendation: {report['recommendation']}")
        else:
            logger.info("✓ No data drift detected")
        
        return is_drift, report
    
    def _calculate_statistics(self, data: np.ndarray) -> Dict:
        """
        Calculate statistical properties
        
        WHY THESE STATS:
            Mean: Central tendency
            Std: Spread
            Skew: Asymmetry
            Kurtosis: Tail heaviness
            
        Together they characterize distribution
        
        Args:
            data: Input data
            
        Returns:
            Statistics dictionary
        """
        return {
            'mean': np.mean(data, axis=0),
            'std': np.std(data, axis=0),
            'skew': stats.skew(data, axis=0),
            'kurtosis': stats.kurtosis(data, axis=0)
        }
    
    def _ks_test(self, current_data: np.ndarray) -> Dict:
        """
        Kolmogorov-Smirnov test
        
        WHY KS TEST:
            Tests if samples from same distribution
            Non-parametric (no assumptions)
            Sensitive to location and shape
        
        NULL HYPOTHESIS:
            Baseline and current from same distribution
        
        INTERPRETATION:
            p < 0.05: Reject null, distributions differ
            p >= 0.05: Cannot reject null, similar distributions
        
        Args:
            current_data: Current data
            
        Returns:
            Test results
        """
        # Flatten for univariate test
        # WHY FLATTEN:
        # KS test is univariate
        # For multivariate, test each dimension
        baseline_flat = self.baseline_data.flatten()
        current_flat = current_data.flatten()
        
        statistic, p_value = stats.ks_2samp(baseline_flat, current_flat)
        
        return {
            'test': 'kolmogorov_smirnov',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'is_drift': p_value < self.threshold
        }
    
    def _population_stability_index(self, current_data: np.ndarray) -> Dict:
        """
        Calculate Population Stability Index
        
        WHY PSI:
            Industry standard
            Easy to interpret
            Quantifies distribution shift
        
        FORMULA:
            PSI = Σ (current% - baseline%) * ln(current% / baseline%)
        
        INTERPRETATION:
            PSI < 0.1: No significant change
            0.1 <= PSI < 0.2: Moderate change
            PSI >= 0.2: Significant change
        
        Args:
            current_data: Current data
            
        Returns:
            PSI results
        """
        # Create bins
        # WHY 10 BINS:
        # Balance between granularity and stability
        # Standard choice
        n_bins = 10
        bins = np.linspace(
            self.baseline_data.min(),
            self.baseline_data.max(),
            n_bins + 1
        )
        
        # Calculate distributions
        baseline_dist, _ = np.histogram(self.baseline_data.flatten(), bins=bins)
        current_dist, _ = np.histogram(current_data.flatten(), bins=bins)
        
        # Normalize
        baseline_dist = baseline_dist / baseline_dist.sum()
        current_dist = current_dist / current_dist.sum()
        
        # Add small constant to avoid log(0)
        # WHY EPSILON:
        # Prevent division by zero
        # Minimal impact on result
        epsilon = 1e-10
        baseline_dist = baseline_dist + epsilon
        current_dist = current_dist + epsilon
        
        # Calculate PSI
        psi = np.sum(
            (current_dist - baseline_dist) * np.log(current_dist / baseline_dist)
        )
        
        return {
            'metric': 'population_stability_index',
            'value': float(psi),
            'is_drift': psi >= 0.2  # WHY 0.2: Standard threshold
        }
    
    def _check_statistical_moments(self, current_data: np.ndarray) -> Dict:
        """
        Check statistical moments for drift
        
        WHY MOMENTS:
            Capture different aspects of distribution
            Mean: Location
            Std: Scale
            Skew: Asymmetry
            Kurtosis: Tails
        
        Args:
            current_data: Current data
            
        Returns:
            Moments comparison
        """
        current_stats = self._calculate_statistics(current_data)
        
        # Calculate relative changes
        # WHY RELATIVE:
        # Scale-independent
        # Easy to interpret
        mean_change = np.abs(
            (current_stats['mean'] - self.baseline_stats['mean']) /
            (self.baseline_stats['mean'] + 1e-10)
        ).mean()
        
        std_change = np.abs(
            (current_stats['std'] - self.baseline_stats['std']) /
            (self.baseline_stats['std'] + 1e-10)
        ).mean()
        
        # WHY 10% THRESHOLD:
        # Significant but not overly sensitive
        # Adjustable based on requirements
        is_drift = (mean_change > 0.1) or (std_change > 0.1)
        
        return {
            'mean_change': float(mean_change),
            'std_change': float(std_change),
            'is_drift': is_drift
        }
    
    def _check_feature_drift(
        self,
        current_data: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> Dict:
        """
        Check drift for individual features
        
        WHY FEATURE-WISE:
            Identifies problematic features
            Actionable insights
            Helps debugging
        
        Args:
            current_data: Current data
            feature_names: Feature names
            
        Returns:
            Per-feature drift results
        """
        n_features = current_data.shape[1] if len(current_data.shape) > 1 else 1
        
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]
        
        drifted_features = []
        
        for i in range(n_features):
            baseline_feature = self.baseline_data[:, i]
            current_feature = current_data[:, i]
            
            # KS test per feature
            _, p_value = stats.ks_2samp(baseline_feature, current_feature)
            
            if p_value < self.threshold:
                drifted_features.append({
                    'name': feature_names[i],
                    'p_value': float(p_value)
                })
        
        return {
            'drifted_features': drifted_features,
            'is_drift': len(drifted_features) > 0
        }
    
    def _calculate_severity(self, drift_signals: Dict) -> str:
        """
        Calculate drift severity
        
        WHY SEVERITY:
            Prioritize response
            Different actions for different severities
        
        Args:
            drift_signals: Detected drift signals
            
        Returns:
            Severity level
        """
        drift_count = sum(
            1 for signal in drift_signals.values()
            if signal.get('is_drift', False)
        )
        
        if drift_count == 0:
            return "NONE"
        elif drift_count == 1:
            return "LOW"
        elif drift_count == 2:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _get_recommendation(self, drift_signals: Dict) -> str:
        """Get actionable recommendation"""
        severity = self._calculate_severity(drift_signals)
        
        if severity == "HIGH":
            return (
                "CRITICAL: Multiple drift signals detected. "
                "Investigate data source immediately. "
                "Consider retraining model."
            )
        elif severity == "MEDIUM":
            return (
                "WARNING: Moderate drift detected. "
                "Monitor closely. Prepare for retraining."
            )
        elif severity == "LOW":
            return (
                "NOTICE: Minor drift detected. "
                "Continue monitoring."
            )
        else:
            return "No action needed."


__all__ = ['DataDriftDetector']
