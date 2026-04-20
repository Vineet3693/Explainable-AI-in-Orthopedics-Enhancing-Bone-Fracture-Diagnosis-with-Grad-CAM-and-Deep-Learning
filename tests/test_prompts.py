"""
Test Prompts - Unit Tests for Prompt Templates

PURPOSE:
    Tests prompt generation functions to ensure correct output.
    Validates prompt structure and content.

WHY TEST PROMPTS:
    Bad prompts: Poor LLM responses, wasted money
    Testing ensures: Correct structure, complete content
    
    IMPACT: Better prompts, fewer errors

USAGE:
    pytest tests/test_prompts.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.prompts.gemini.report_generation import generate_radiology_report_prompt
from src.prompts.groq.summary_prompts import generate_patient_summary_prompt


class TestGeminiPrompts:
    """Test Gemini prompt generation"""
    
    def test_radiology_report_prompt_structure(self):
        """Test that radiology report prompt has required sections"""
        prompt = generate_radiology_report_prompt(
            prediction='fracture',
            confidence=0.95,
            anatomy='wrist',
            image_quality=85
        )
        
        # WHY CHECK FOR SECTIONS:
        # Prompt must include all required sections
        # Missing sections = incomplete reports
        assert 'CLINICAL INFORMATION' in prompt
        assert 'FINDINGS' in prompt
        assert 'IMPRESSION' in prompt
        assert 'RECOMMENDATIONS' in prompt
        assert 'DISCLAIMER' in prompt
    
    def test_prompt_includes_patient_data(self):
        """Test that patient data is included when provided"""
        prompt = generate_radiology_report_prompt(
            prediction='fracture',
            confidence=0.95,
            anatomy='wrist',
            image_quality=85,
            patient_age=45,
            patient_gender='male'
        )
        
        assert '45' in prompt
        assert 'male' in prompt


class TestGroqPrompts:
    """Test Groq prompt generation"""
    
    def test_summary_prompt_structure(self):
        """Test patient summary prompt structure"""
        prompt = generate_patient_summary_prompt(
            report='Patient has wrist fracture',
            language='english'
        )
        
        assert 'english' in prompt.lower()
        assert 'fracture' in prompt.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
