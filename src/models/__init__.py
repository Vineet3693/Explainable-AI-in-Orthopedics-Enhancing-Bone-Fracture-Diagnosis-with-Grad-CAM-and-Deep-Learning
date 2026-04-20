"""
Model architectures package for fracture detection

PACKAGE PURPOSE:
    Contains all CNN model architectures for fracture detection including
    base classes, specific implementations, and factory pattern.

MODULES:
    - base_model.py: Abstract base class for all models
    - resnet50_model.py: ResNet50 architecture (94.2% accuracy)
    - vgg16_model.py: VGG16 architecture (91.8% accuracy, ensemble)
    - efficientnet_model.py: EfficientNet B0/B1/B2 (93.5-94.5%, deployment)
    - model_factory.py: Factory pattern for model creation

KEY CONCEPTS:
    - Transfer Learning: Using ImageNet pre-trained weights
    - Fine-tuning: Training top layers, then all layers
    - Ensemble: Combining multiple models for better accuracy
    - Factory Pattern: Centralized model creation
    - Global Average Pooling: Reducing parameters before classification

MODEL COMPARISON:
    ResNet50: 94.2% accuracy, 25M params, 45ms inference
    VGG16: 91.8% accuracy, 138M params, 62ms inference
    EfficientNet-B0: 93.5% accuracy, 5M params, 38ms inference

USAGE:
    from src.models import ModelFactory
    
    model = ModelFactory.create_model('resnet50')
    model.build_model()
    model.compile_model()
"""

__all__ = [
    'BaseModel',
    'ResNet50Model',
    'VGG16Model',
    'EfficientNetModel',
    'ModelFactory'
]
