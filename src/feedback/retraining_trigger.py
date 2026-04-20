"""
Retraining Trigger for Model Improvement

PURPOSE:
    Monitors feedback and performance metrics to decide when to trigger model retraining.
    Implements logic for active learning loops.

WHY RETRAINING TRIGGER:
    Static models degrade. We need a systematic way to start retraining
    based on accumulated fresh data (corrections) or performance drops.

USAGE:
    from src.feedback.retraining_trigger import RetrainingTrigger

    trigger = RetrainingTrigger(threshold=100)
    should_retrain = trigger.check_trigger()
"""

import logging
import os
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RetrainingTrigger:
    """Determines when to trigger model retraining"""

    def __init__(
        self,
        corrections_dir: str = 'data/corrections',
        count_threshold: int = 100,
        drift_threshold: float = 0.05
    ):
        """
        Initialize trigger logic

        Args:
            corrections_dir: Directory where corrections are stored
            count_threshold: Number of new samples required to trigger
            drift_threshold: Performance drop required to trigger
        """
        self.corrections_dir = corrections_dir
        self.count_threshold = count_threshold
        self.drift_threshold = drift_threshold
        self.trigger_state_file = os.path.join(corrections_dir, 'trigger_state.json')

    def check_trigger(self, current_performance: float = None) -> Dict[str, Any]:
        """
        Check if retraining should be triggered

        Args:
            current_performance: Optional current metric (e.g., accuracy)
        
        Returns:
            Dict with trigger status and reason
        """
        # 1. Check Data Volume
        new_samples = self._count_new_samples()
        
        if new_samples >= self.count_threshold:
            logger.info(f"Retraining triggered: {new_samples} new samples (threshold: {self.count_threshold})")
            return {
                'trigger': True,
                'reason': 'data_volume',
                'details': f'{new_samples} new samples'
            }

        # 2. Check Concept Drift (if performance provided)
        if current_performance is not None:
            baseline = self._get_baseline_performance()
            drop = baseline - current_performance
            
            if drop > self.drift_threshold:
                logger.warning(f"Retraining triggered: Performance drop {drop:.2%} (threshold: {self.drift_threshold:.2%})")
                return {
                    'trigger': True,
                    'reason': 'performance_drift',
                    'details': f'Performance dropped by {drop:.2f}'
                }

        return {'trigger': False, 'reason': None}

    def _count_new_samples(self) -> int:
        """Count corrections since last retrain"""
        log_file = os.path.join(self.corrections_dir, 'corrections_log.jsonl')
        if not os.path.exists(log_file):
            return 0
            
        # In a real system, we'd track lined read vs lines collected.
        # Here we just count total lines for simplicity or count lines 
        # timestamped after the last retrain.
        last_retrain = self._get_last_retrain_time()
        count = 0
        import dateutil.parser

        try:
            with open(log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    # Simple counting relative to last reset would be better
                    # but for now we simulate counting 'new' valid entries
                    entry_time = dateutil.parser.parse(entry['timestamp']).timestamp()
                    if entry_time > last_retrain:
                        count += 1
        except Exception:
            # Fallback simple count if parsing fails
            return 0
            
        return count

    def _get_last_retrain_time(self) -> float:
        """Get timestamp of last retraining event"""
        if os.path.exists(self.trigger_state_file):
            with open(self.trigger_state_file, 'r') as f:
                data = json.load(f)
                return data.get('last_retrain_timestamp', 0.0)
        return 0.0

    def _get_baseline_performance(self) -> float:
        """Get baseline performance metric"""
        # Placeholder: Read from model training metadata
        return 0.95

    def reset_trigger(self):
        """Reset trigger state after successful retraining"""
        import time
        state = {
            'last_retrain_timestamp': time.time(),
            'samples_at_last_retrain': 0 # Simplification
        }
        with open(self.trigger_state_file, 'w') as f:
            json.dump(state, f)
        logger.info("Retraining trigger reset")


__all__ = ['RetrainingTrigger']
