"""
Test Structured Outputs - Tests for Pydantic Models

PURPOSE:
    Tests Pydantic models for LLM response parsing.
    Ensures models validate correctly.

USAGE:
    pytest tests/test_structured_outputs.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.prompts.structured_outputs import RadiologyReport, PatientSummary
from pydantic import ValidationError


class TestRadiologyReport:
    """Test RadiologyReport model"""
    
    def test_valid_report(self):
        """Test that valid data passes validation"""
        report = RadiologyReport(
            clinical_information="45yo male, wrist pain",
            technique="AP and lateral views",
            findings="Fracture of distal radius",
            impression="Distal radius fracture",
            recommendations="Orthopedic consult",
            confidence=0.95
        )
        
        assert report.confidence == 0.95
        assert 'fracture' in report.findings.lower()
    
    def test_invalid_confidence_fails(self):
        """Test that invalid confidence fails"""
        with pytest.raises(ValidationError):
            RadiologyReport(
                clinical_information="Test",
                technique="Test",
                findings="Test",
                impression="Test",
                recommendations="Test",
                confidence=1.5  # Invalid: > 1.0
            )


class TestPatientSummary:
    """Test PatientSummary model"""
    
    def test_valid_summary(self):
        """Test valid patient summary"""
        summary = PatientSummary(
            what_we_found="Wrist fracture",
            what_it_means="Needs treatment",
            next_steps=["See doctor", "Get cast"],
            timeline="6-8 weeks"
        )
        
        assert len(summary.next_steps) == 2
        assert summary.timeline == "6-8 weeks"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
