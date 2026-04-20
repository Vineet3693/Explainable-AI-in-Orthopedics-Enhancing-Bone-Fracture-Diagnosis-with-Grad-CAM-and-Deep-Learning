"""
Model Factory for creating CNN models

PURPOSE:
    Centralized factory for creating and configuring all CNN model architectures.
    Simplifies model creation and ensures consistent configuration.

SUPPORTED MODELS:
    - resnet50: ResNet50 (94.2% accuracy, recommended)
    - vgg16: VGG16 (91.8% accuracy, ensemble)
    - efficientnet_b0/b1/b2: EfficientNet variants (93.5-94.5%, deployment)
    - ensemble: Combination of multiple models

FACTORY PATTERN BENEFITS:
    - Centralized model creation
    - Consistent configuration
    - Easy to add new models
    - Simplified testing
"""

from typing import Optional, Dict, Any
import logging
from src.models.base_model import BaseModel
from src.models.resnet50_model import ResNet50Model
from src.models.vgg16_model import VGG16Model
from src.models.efficientnet_model import EfficientNetModel

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory for creating CNN models"""
    
    # Registry of available models
    _models = {
        'resnet50': ResNet50Model,
        'vgg16': VGG16Model,
        'efficientnet_b0': lambda **kwargs: EfficientNetModel(variant='b0', **kwargs),
        'efficientnet_b1': lambda **kwargs: EfficientNetModel(variant='b1', **kwargs),
        'efficientnet_b2': lambda **kwargs: EfficientNetModel(variant='b2', **kwargs),
    }
    
    @classmethod
    def create_model(
        cls,
        model_name: str,
        input_size: tuple = (224, 224),
        num_classes: int = 1,
        **kwargs
    ) -> BaseModel:
        """
        Create a model instance
        
        Args:
            model_name: Name of model ('resnet50', 'vgg16', 'efficientnet_b0', etc.)
            input_size: Input image size (height, width)
            num_classes: Number of output classes (1 for binary classification)
            **kwargs: Additional model-specific arguments
            
        Returns:
            Model instance
            
        Example:
            >>> model = ModelFactory.create_model('resnet50')
            >>> model.build_model()
            >>> model.compile_model()
        """
        if model_name not in cls._models:
            available = ', '.join(cls._models.keys())
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available models: {available}"
            )
        
        logger.info(f"Creating model: {model_name}")
        
        # Create model instance
        model_class = cls._models[model_name]
        if callable(model_class):
            model = model_class(
                input_size=input_size,
                num_classes=num_classes,
                **kwargs
            )
        else:
            model = model_class(
                input_size=input_size,
                num_classes=num_classes,
                **kwargs
            )
        
        return model
    
    @classmethod
    def list_models(cls) -> list:
        """List all available models"""
        return list(cls._models.keys())


__all__ = ['ModelFactory']
