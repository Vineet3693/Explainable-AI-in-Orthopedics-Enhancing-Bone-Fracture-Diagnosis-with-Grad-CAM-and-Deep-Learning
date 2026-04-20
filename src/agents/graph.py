"""
LangGraph Workflow Graph Builder

PURPOSE:
    Builds complete LangGraph workflow graphs.
    Combines nodes and edges into executable workflows.

WHY LANGGRAPH:
    Sequential code: Hard to modify, no visualization
    LangGraph: Visual workflows, easy to modify, reusable
    
    IMPACT: Flexible workflows, easier maintenance

DESIGN PHILOSOPHY:
    1. Modular nodes
    2. Clear edges
    3. Error handling
    4. Easy to visualize

USAGE:
    from src.agents.graph import build_diagnosis_graph
    
    graph = build_diagnosis_graph()
    result = graph.invoke({'image_path': 'xray.jpg'})
"""

from langgraph.graph import StateGraph, END
from src.agents.state import DiagnosisState
from src.agents.nodes import (
    validate_image_node,
    predict_fracture_node,
    generate_report_node
)
from src.agents.edges import should_validate, should_generate_report
import logging

logger = logging.getLogger(__name__)


def build_diagnosis_graph() -> StateGraph:
    """
    Build diagnosis workflow graph
    
    WHY THIS STRUCTURE:
        1. Validate image first (catch bad images early)
        2. Predict fracture (core task)
        3. Generate report (output)
        4. Conditional routing (skip steps if needed)
    
    Returns:
        Compiled workflow graph
    """
    # WHY StateGraph:
    # Manages state across nodes
    # Ensures type safety
    # Tracks execution
    graph = StateGraph(DiagnosisState)
    
    # Add nodes
    graph.add_node("validate", validate_image_node)
    graph.add_node("predict", predict_fracture_node)
    graph.add_node("generate_report", generate_report_node)
    
    # Add edges
    graph.set_entry_point("validate")
    
    # WHY CONDITIONAL EDGES:
    # Skip prediction if validation fails
    # Skip report if no prediction
    graph.add_conditional_edges(
        "validate",
        should_validate,
        {
            "predict": "predict",
            "end": END
        }
    )
    
    graph.add_conditional_edges(
        "predict",
        should_generate_report,
        {
            "generate_report": "generate_report",
            "end": END
        }
    )
    
    graph.add_edge("generate_report", END)
    
    # Compile graph
    compiled_graph = graph.compile()
    
    logger.info("Diagnosis graph built successfully")
    
    return compiled_graph


__all__ = ['build_diagnosis_graph']
