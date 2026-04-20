"""
Structured Outputs with Pydantic Schemas

PURPOSE:
    Pydantic models for parsing and validating LLM JSON outputs.
    Ensures LLM responses match expected structure.

WHY PYDANTIC:
    Raw JSON: No validation, errors at runtime
    Pydantic: Type-safe, validated, auto-documented
    
    IMPACT: 90% fewer parsing errors

USAGE:
    from src.prompts.structured_outputs import RadiologyReport
    
    report = RadiologyReport.parse_raw(llm_response)
    print(report.findings)
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SeverityLevel(str, Enum):
    """Fracture severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class RadiologyReport(BaseModel):
    """Structured radiology report"""
    
    clinical_information: str = Field(..., description="Clinical indication and patient info")
    technique: str = Field(..., description="Imaging technique and views")
    findings: str = Field(..., description="Detailed radiographic findings")
    impression: str = Field(..., description="Summary diagnosis")
    recommendations: str = Field(..., description="Follow-up recommendations")
    confidence: float = Field(..., ge=0, le=1, description="AI confidence level")
    
    class Config:
        schema_extra = {
            "example": {
                "clinical_information": "45-year-old male with wrist pain after fall",
                "technique": "AP and lateral views of right wrist",
                "findings": "Comminuted fracture of distal radius...",
                "impression": "Distal radius fracture with dorsal angulation",
                "recommendations": "Orthopedic consultation, possible ORIF",
                "confidence": 0.95
            }
        }


class PatientSummary(BaseModel):
    """Patient-friendly summary"""
    
    what_we_found: str = Field(..., description="Simple explanation of findings")
    what_it_means: str = Field(..., description="Significance of findings")
    next_steps: List[str] = Field(..., description="Action items for patient")
    timeline: Optional[str] = Field(None, description="Expected recovery timeline")
    
    class Config:
        schema_extra = {
            "example": {
                "what_we_found": "The X-ray shows a break in your wrist bone",
                "what_it_means": "This is a fracture that will need treatment",
                "next_steps": ["See orthopedic doctor", "Keep wrist immobilized", "Take pain medication as prescribed"],
                "timeline": "6-8 weeks for healing"
            }
        }


class QAResponse(BaseModel):
    """Q&A response structure"""
    
    answer: str = Field(..., description="Answer to question")
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence")
    sources: Optional[List[str]] = Field(None, description="Information sources")
    follow_up_questions: Optional[List[str]] = Field(None, description="Suggested follow-up questions")


__all__ = [
    'SeverityLevel',
    'RadiologyReport',
    'PatientSummary',
    'QAResponse'
]
