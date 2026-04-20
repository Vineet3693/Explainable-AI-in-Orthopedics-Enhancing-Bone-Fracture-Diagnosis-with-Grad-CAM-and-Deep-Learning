"""
Explainability package for AI model interpretability

PACKAGE PURPOSE:
    Contains modules for generating visual explanations of model predictions.
    Critical for building trust with radiologists and ensuring model learns
    correct features.

MODULES:
    - gradcam.py: Grad-CAM (Gradient-weighted Class Activation Mapping)

KEY CONCEPTS:
    - Grad-CAM: Visual explanation showing where model focused
    - Heatmap: Color-coded visualization (red=high focus, blue=low focus)
    - Explainable AI (XAI): Making AI decisions interpretable
    - Class Activation Map: Highlighting important image regions
    - Feature Maps: Internal CNN representations

WHY EXPLAINABILITY MATTERS:
    - Trust: Radiologists can verify model reasoning
    - Debugging: Identify if model focuses on artifacts
    - Compliance: Medical AI regulations require explainability
    - Safety: Catch model learning wrong features
    - Education: Understand what model learned

GRAD-CAM INTERPRETATION:
    RED regions: Model focused here strongly (should be fracture site)
    YELLOW regions: Moderate focus
    BLUE regions: Low focus
    
    GOOD: Heatmap highlights fracture location
    BAD: Heatmap highlights labels, markers, or edges

USAGE:
    from src.explainability import GradCAM
    
    gradcam = GradCAM(model, layer_name='conv5_block3_out')
    heatmap = gradcam.generate_heatmap(image, class_idx=1)
    overlay = gradcam.overlay_heatmap(image, heatmap)
"""

__all__ = [
    'GradCAM',
    'generate_heatmap',
    'overlay_heatmap'
]
