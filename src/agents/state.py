"""
LangGraph State Definitions

PURPOSE:
    Defines state schemas for LangGraph workflows.
    Ensures type-safe state management across workflow nodes.

USAGE:
    from src.agents.state import DiagnosisState
    
    state = DiagnosisState(
        image_path='xray.jpg',
        prediction=None
    )
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class DiagnosisState(BaseModel):
    """State for diagnosis workflow"""
    
    # Input
    image_path: str
    patient_info: Optional[Dict[str, Any]] = None
    
    # Validation
    is_valid: Optional[bool] = None
    validation_results: Optional[Dict[str, Any]] = None
    
    # Prediction
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    
    # Report
    report: Optional[str] = None
    
    # Q&A
    questions: Optional[List[str]] = None
    answers: Optional[List[str]] = None
    
    class Config:
        arbitrary_types_allowed = True


class WorkflowState(BaseModel):
    """Generic workflow state"""
    
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    metadata: Dict[str, Any] = {}


__all__ = ['DiagnosisState', 'WorkflowState']
