"""
Feedback Analytics for Insights

PURPOSE:
    Analyzes collected feedback to generate insights on model performance.
    Identifies common failure modes and confusing cases.

USAGE:
    from src.feedback.feedback_analytics import FeedbackAnalytics

    analytics = FeedbackAnalytics()
    report = analytics.generate_report()
    print(report['average_rating'])
"""

import logging
import json
import os
from typing import Dict, Any, List
from collections import Counter
import statistics

logger = logging.getLogger(__name__)


class FeedbackAnalytics:
    """Analyzes user feedback data"""

    def __init__(self, feedback_dir: str = 'logs/feedback'):
        self.feedback_dir = feedback_dir

    def generate_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate analytics report from feedback logs
        
        Args:
            days: Analysis window in days
            
        Returns:
            Dictionary containing feedback metrics
        """
        feedback_data = self._load_feedback(days)
        
        if not feedback_data:
            return {
                'total_feedback': 0,
                'status': 'no_data'
            }

        report = {
            'total_feedback': len(feedback_data),
            'ratings': self._analyze_ratings(feedback_data),
            'agreement_rate': self._calculate_agreement(feedback_data),
            'common_issues': self._analyze_comments(feedback_data)
        }
        
        return report

    def _load_feedback(self, days: int) -> List[Dict[str, Any]]:
        """Load feedback files"""
        data = []
        # In a real impl, iterate over files in dir matching date range.
        # Placeholder for directory scan:
        try:
            if not os.path.exists(self.feedback_dir):
                return []
                
            for filename in os.listdir(self.feedback_dir):
                if filename.endswith('.jsonl'):
                    path = os.path.join(self.feedback_dir, filename)
                    with open(path, 'r') as f:
                        for line in f:
                            try:
                                data.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error analyzing feedback: {e}")
            
        return data

    def _analyze_ratings(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate rating statistics"""
        # Filter entries with ratings
        ratings = [f['rating'] for f in data if f.get('rating') is not None]
        
        if not ratings:
            return {'average': 0.0, 'count': 0}
            
        return {
            'average': statistics.mean(ratings),
            'min': min(ratings),
            'max': max(ratings),
            'count': len(ratings)
        }

    def _calculate_agreement(self, data: List[Dict[str, Any]]) -> float:
        """Calculate AI-Human agreement rate"""
        # Look for explicit agreement flags or inferred agreement
        agreements = [f for f in data if f.get('is_correct') is True]
        disagreements = [f for f in data if f.get('is_correct') is False]
        
        total_validated = len(agreements) + len(disagreements)
        
        if total_validated == 0:
            return 0.0
            
        return len(agreements) / total_validated

    def _analyze_comments(self, data: List[Dict[str, Any]]) -> List[str]:
        """Extract common themes from comments (naïve approach)"""
        # In reality, use NLP clustering
        comments = [f['comment'] for f in data if f.get('comment')]
        return comments[:5] # Return sample recent comments


__all__ = ['FeedbackAnalytics']
