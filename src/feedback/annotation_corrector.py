"""
Annotation Corrector for Refining AI Annotations

PURPOSE:
    Allows processing and storage of user corrections to AI annotations.
    bridges the gap between AI predictions and ground truth.

WHY ANNOTATION CORRECTOR:
    AI is not perfect. Capturing expert corrections is vital for:
    1. Immediate accuracy (for the report)
    2. Long-term improvement (retraining data)

USAGE:
    from src.feedback.annotation_corrector import AnnotationCorrector

    corrector = AnnotationCorrector()
    corrector.save_correction(
        image_id="img123",
        original_box=[100, 100, 200, 200],
        corrected_box=[105, 95, 205, 205],
        user_id="doc_smith"
    )
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)


class AnnotationCorrector:
    """Manages corrections to annotations"""

    def __init__(self, corrections_dir: str = 'data/corrections'):
        self.corrections_dir = corrections_dir
        os.makedirs(corrections_dir, exist_ok=True)

    def save_correction(
        self,
        image_id: str,
        original_annotation: Any,
        corrected_annotation: Any,
        user_id: str,
        annotation_type: str = "bounding_box"
    ):
        """
        Save a user correction

        Args:
            image_id: Unique image identifier
            original_annotation: What the AI predicted
            corrected_annotation: What the user corrected it to
            user_id: User making the correction
            annotation_type: Type of annotation (box, polygon, label)
        """
        correction_entry = {
            'timestamp': datetime.now().isoformat(),
            'image_id': image_id,
            'user_id': user_id,
            'type': annotation_type,
            'original': original_annotation,
            'corrected': corrected_annotation
        }

        # WHY JSON LINES:
        # Appending is efficient.
        # Each line is a self-contained record.
        file_path = os.path.join(self.corrections_dir, 'corrections_log.jsonl')
        
        try:
            with open(file_path, 'a') as f:
                f.write(json.dumps(correction_entry) + '\n')
            
            logger.info(f"Correction saved for image {image_id} by {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to save correction: {e}")
            raise

    def get_corrections(self, image_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve corrections, optionally filtered by image_id
        
        Args:
            image_id: Filter by image ID
            
        Returns:
            List of correction entries
        """
        corrections = []
        file_path = os.path.join(self.corrections_dir, 'corrections_log.jsonl')
        
        if not os.path.exists(file_path):
            return []

        try:
            with open(file_path, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    if image_id is None or entry['image_id'] == image_id:
                        corrections.append(entry)
        except Exception as e:
            logger.error(f"Error reading corrections: {e}")
            
        return corrections


__all__ = ['AnnotationCorrector']
