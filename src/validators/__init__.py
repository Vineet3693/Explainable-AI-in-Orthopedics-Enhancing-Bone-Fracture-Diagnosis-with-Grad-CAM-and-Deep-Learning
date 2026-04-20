"""
Validation package for image quality and content verification

PACKAGE PURPOSE:
    Contains all validation modules for ensuring only valid, high-quality
    X-ray images reach the fracture detection model. Implements 4-stage
    validation pipeline for patient safety.

MODULES:
    - image_validator.py: Master validator orchestrating all checks
    - format_validator.py: File format and size validation (~5ms)
    - xray_classifier.py: X-ray vs non-X-ray classification (~50ms)
    - anatomy_detector.py: Bone/body part detection (~100ms)
    - quality_checker.py: Image quality assessment (~50ms)

VALIDATION PIPELINE (4 STAGES):
    Stage 1: FORMAT (~5ms) - File format, size, dimensions
    Stage 2: X-RAY (~50ms) - Verify it's an X-ray image
    Stage 3: ANATOMY (~100ms) - Identify bone type
    Stage 4: QUALITY (~50ms) - Check blur, noise, contrast
    
    Total: ~200ms, Rejection rate: ~40-50% of uploads

KEY CONCEPTS:
    - Fail Fast: Reject early to save computation
    - Defense in Depth: Multiple validation layers
    - MobileNetV3: Lightweight CNN for classification
    - Laplacian Variance: Blur detection metric
    - DICOM: Medical imaging standard format

USAGE:
    from src.validators import ImageValidator
    
    validator = ImageValidator()
    is_valid, results = validator.validate('xray.jpg')
"""

__all__ = [
    'ImageValidator',
    'FormatValidator',
    'XRayClassifier',
    'AnatomyDetector',
    'QualityChecker'
]
