"""
Model Logger for CNN Prediction Logging

PURPOSE:
    Logs all CNN model predictions with input/output details.
    Essential for model monitoring and debugging.

WHY MODEL LOGGING:
    Track model performance, detect drift, debug errors
    
    IMPACT: Better model monitoring, faster debugging

USAGE:
    from src.monitoring.logging.model_logger import ModelLogger
    
    logger = ModelLogger()
    logger.log_prediction(
        image_id='img123',
        prediction='fracture',
        confidence=0.95,
        model_version='v1.0'
    )
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class ModelLogger:
    """CNN model prediction logger"""
    
    def __init__(self, log_dir: str = 'logs/models'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_prediction(
        self,
        image_id: str,
        prediction: str,
        confidence: float,
        model_version: str,
        anatomy: Optional[str] = None,
        inference_time: Optional[float] = None,
        gradcam_generated: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log model prediction
        
        WHY LOG PREDICTIONS:
            - Track model performance over time
            - Detect model drift
            - Debug prediction errors
            - Analyze confidence distributions
        
        Args:
            image_id: Image identifier
            prediction: Model prediction
            confidence: Prediction confidence (0-1)
            model_version: Model version used
            anatomy: Detected anatomy
            inference_time: Inference duration
            gradcam_generated: Whether Grad-CAM was generated
            metadata: Additional metadata
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'image_id': image_id,
            'prediction': prediction,
            'confidence': confidence,
            'model_version': model_version,
            'anatomy': anatomy,
            'inference_time_seconds': inference_time,
            'gradcam_generated': gradcam_generated,
            'metadata': metadata or {}
        }
        
        # Write to daily log file
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.log_dir, f'cnn_predictions_{date_str}.jsonl')
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.debug(
            f"Prediction logged: {prediction} ({confidence:.2%}) - {image_id}"
        )


__all__ = ['ModelLogger']
