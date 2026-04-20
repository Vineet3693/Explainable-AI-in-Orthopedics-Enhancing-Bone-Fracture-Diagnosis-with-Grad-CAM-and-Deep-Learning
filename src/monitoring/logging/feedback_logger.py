"""
Feedback Logger for User Feedback Logging

PURPOSE:
    Logs user feedback on predictions for model improvement.
    Tracks corrections, ratings, and comments.

USAGE:
    from src.monitoring.logging.feedback_logger import FeedbackLogger
    
    logger = FeedbackLogger()
    logger.log_feedback(
        image_id='img123',
        ai_prediction='fracture',
        user_correction='normal',
        rating=2
    )
"""

import json
import logging
from datetime import datetime
from typing import Optional
import os

logger = logging.getLogger(__name__)


class FeedbackLogger:
    """User feedback logger"""
    
    def __init__(self, log_dir: str = 'logs/feedback'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_feedback(
        self,
        image_id: str,
        ai_prediction: str,
        user_correction: Optional[str] = None,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log user feedback"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'image_id': image_id,
            'ai_prediction': ai_prediction,
            'user_correction': user_correction,
            'rating': rating,
            'comment': comment,
            'user_id': user_id,
            'is_correct': ai_prediction == user_correction if user_correction else None
        }
        
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.log_dir, f'feedback_{date_str}.jsonl')
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"Feedback logged for {image_id}")


__all__ = ['FeedbackLogger']
