"""
Validation Node for LangGraph

PURPOSE:
    Dedicated validation node for LangGraph workflows.
    Validates images before processing.

WHY SEPARATE NODE:
    Reusable across workflows
    Clear separation of concerns
    Easy to test
    
USAGE:
    from src.agents.validation_node import validation_node
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate image node
    
    WHY VALIDATION NODE:
        Catch bad images early
        Save compute on invalid images
        Provide clear error messages
    
    Args:
        state: Workflow state with image_path
        
    Returns:
        Updated state with validation results
    """
    logger.info("Validating image...")
    
    image_path = state.get('image_path')
    
    # Placeholder validation logic
    # In production, would use actual ImageValidator
    is_valid = True
    validation_results = {
        'format': 'valid',
        'size': 'valid',
        'quality_score': 85
    }
    
    # WHY UPDATE STATE:
    # Next nodes need validation results
    # Conditional edges use is_valid
    state['is_valid'] = is_valid
    state['validation_results'] = validation_results
    
    if is_valid:
        logger.info("✓ Image validation passed")
    else:
        logger.warning("✗ Image validation failed")
    
    return state


__all__ = ['validation_node']
