"""
Annotation package for data annotation tools

PACKAGE PURPOSE:
    Contains tools for annotating X-ray images with fracture locations,
    severity, and other metadata. Used for creating training datasets.

POTENTIAL MODULES:
    - annotation_tool.py: GUI for manual annotation
    - auto_annotation.py: Semi-automated annotation
    - annotation_validator.py: Validate annotation quality
    - export_annotations.py: Export to various formats

KEY CONCEPTS:
    - Bounding Box: Rectangle around fracture location
    - Segmentation: Pixel-level fracture outline
    - Classification: Fracture type and severity
    - Inter-annotator Agreement: Consistency between annotators
    - COCO Format: Common annotation format

ANNOTATION WORKFLOW:
    1. Load X-ray image
    2. Draw bounding boxes around fractures
    3. Label fracture type and severity
    4. Review and validate annotations
    5. Export to training format

NOTE: This is a placeholder for future annotation tools.
      Current system uses pre-annotated datasets.

USAGE (Future):
    from src.annotation import AnnotationTool
    
    tool = AnnotationTool()
    tool.annotate_image('xray.jpg')
"""

__all__ = []  # No annotation tools implemented yet
