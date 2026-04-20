"""
User Feedback Collector

PURPOSE:
    Collects feedback from radiologists and doctors on AI predictions.
    Used for continuous model improvement.

USAGE:
    from src.feedback.user_feedback_collector import FeedbackCollector
    
    collector = FeedbackCollector()
    collector.collect_feedback(
        image_id='12345',
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


class FeedbackCollector:
    """Collects user feedback on predictions"""
    
    def __init__(self, feedback_dir: str = 'logs/feedback'):
        self.feedback_dir = feedback_dir
        os.makedirs(feedback_dir, exist_ok=True)
    
    def collect_feedback(
        self,
        image_id: str,
        ai_prediction: str,
        user_correction: Optional[str] = None,
        rating: Optional[int] = None,
        comment: Optional[str] = None
    ):
        """
        Collect feedback
        
        Args:
            image_id: Image identifier
            ai_prediction: AI's prediction
            user_correction: User's correction (if different)
            rating: Quality rating (1-5)
            comment: Optional comment
        """
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'image_id': image_id,
            'ai_prediction': ai_prediction,
            'user_correction': user_correction,
            'rating': rating,
            'comment': comment,
            'is_correct': ai_prediction == user_correction if user_correction else None
        }
        
        # Save to file
        date_str = datetime.now().strftime('%Y%m%d')
        feedback_file = os.path.join(self.feedback_dir, f'feedback_{date_str}.jsonl')
        
        with open(feedback_file, 'a') as f:
            f.write(json.dumps(feedback) + '\n')
        
        logger.info(f"Collected feedback for image {image_id}")


__all__ = ['FeedbackCollector']
