"""
LangGraph Edges Definition

PURPOSE:
    Defines edges (transitions) between nodes in LangGraph workflows.
    Controls workflow execution flow.

WHY EDGES:
    No edges: Nodes don't connect, no workflow
    Edges (this): Define execution order, conditional routing
    
    IMPACT: Flexible workflows, conditional logic

DESIGN PHILOSOPHY:
    1. Clear transition logic
    2. Conditional routing
    3. Error handling paths
    4. Easy to understand

USAGE:
    from src.agents.edges import should_validate, should_generate_report
"""

from typing import Dict, Any


def should_validate(state: Dict[str, Any]) -> str:
    """
    Determine if validation should proceed
    
    WHY CONDITIONAL EDGES:
        Not all images need validation
        Skip validation for trusted sources
        Save time and cost
    
    Args:
        state: Workflow state
        
    Returns:
        Next node name
    """
    # If image already validated, skip
    if state.get('is_valid') is not None:
        return 'predict'
    
    return 'validate'


def should_generate_report(state: Dict[str, Any]) -> str:
    """
    Determine if report should be generated
    
    WHY CONDITIONAL:
        Only generate report if prediction made
        Skip if validation failed
    
    Args:
        state: Workflow state
        
    Returns:
        Next node name
    """
    if not state.get('is_valid', False):
        return 'end'
    
    if state.get('prediction') is None:
        return 'end'
    
    return 'generate_report'


def route_by_prediction(state: Dict[str, Any]) -> str:
    """
    Route based on prediction result
    
    WHY ROUTE BY PREDICTION:
        Different predictions need different handling
        Fracture: Generate detailed report
        Normal: Simple summary
    
    Args:
        state: Workflow state
        
    Returns:
        Next node name
    """
    prediction = state.get('prediction', 'unknown')
    
    if prediction == 'fracture':
        return 'detailed_report'
    elif prediction == 'normal':
        return 'simple_summary'
    else:
        return 'error_handler'


__all__ = [
    'should_validate',
    'should_generate_report',
    'route_by_prediction'
]
