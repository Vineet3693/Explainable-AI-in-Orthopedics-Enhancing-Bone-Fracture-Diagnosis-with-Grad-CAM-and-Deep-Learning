"""
LIME Explainer for Model Interpretability

PURPOSE:
    Implements LIME (Local Interpretable Model-agnostic Explanations).
    Explains predictions by approximating model locally with interpretable model.

WHY LIME:
    Global explanations: May not apply to specific case
    LIME (this): Local explanation for each prediction
    
    IMPACT: Case-specific explanations, better trust

DESIGN PHILOSOPHY:
    1. Model-agnostic (works with any model)
    2. Local fidelity (accurate locally)
    3. Interpretable (uses simple model)
    4. Perturbation-based (samples around instance)

PROS:
    ✅ Model-agnostic (any black-box model)
    ✅ Interpretable (linear model)
    ✅ Local explanations (instance-specific)
    ✅ Well-established method

CONS:
    ❌ Slow (many model calls)
    ❌ Unstable (different runs give different results)
    ❌ Hyperparameter sensitive
    ❌ May not capture global behavior

ALTERNATIVES:
    1. Grad-CAM: Faster but model-specific
    2. Integrated Gradients: Theoretically sound but complex
    3. SHAP: More stable but slower
    4. LIME (this): Good balance for black-box models

COMPARISON:
    | Method    | Model-Agnostic | Speed | Stability | Interpretability |
    |-----------|----------------|-------|-----------|------------------|
    | Grad-CAM  | ❌             | ✅    | ✅        | ✅               |
    | Int. Grad | ❌             | ⚠️    | ✅        | ⚠️               |
    | SHAP      | ✅             | ❌    | ✅        | ⚠️               |
    | LIME      | ✅             | ⚠️    | ⚠️        | ✅               |

USAGE:
    from src.explainability.lime_explainer import LIMEExplainer
    
    explainer = LIMEExplainer(model, predict_fn)
    explanation = explainer.explain_instance(
        image,
        num_samples=1000,
        num_features=10
    )
"""

import numpy as np
from typing import Callable, Tuple, Optional
from lime import lime_image
from skimage.segmentation import mark_boundaries
import logging

logger = logging.getLogger(__name__)


class LIMEExplainer:
    """
    LIME explainer for image classification
    
    WHY LIME:
        Explains predictions by fitting interpretable model
        Works with any black-box model
        Provides local explanations
    """
    
    def __init__(
        self,
        model,
        predict_fn: Optional[Callable] = None
    ):
        """
        Initialize LIME explainer
        
        WHY PREDICT_FN:
            LIME needs function that takes images and returns probabilities
            Wraps model to provide consistent interface
        
        Args:
            model: Model to explain
            predict_fn: Custom prediction function (optional)
        """
        self.model = model
        
        # WHY WRAPPER:
        # LIME expects specific input/output format
        # Wrapper ensures compatibility
        if predict_fn is None:
            self.predict_fn = self._default_predict_fn
        else:
            self.predict_fn = predict_fn
        
        # Initialize LIME
        # WHY THESE PARAMS:
        # kernel_width: Controls locality (smaller = more local)
        # feature_selection: How to select important features
        self.explainer = lime_image.LimeImageExplainer()
        
        logger.info("Initialized LIMEExplainer")
    
    def _default_predict_fn(self, images: np.ndarray) -> np.ndarray:
        """
        Default prediction function
        
        WHY BATCH PROCESSING:
            LIME generates many perturbed images
            Batch processing is much faster
        
        Args:
            images: Batch of images (N, H, W, C)
            
        Returns:
            Probabilities (N, num_classes)
        """
        import torch
        
        # Convert to tensor
        # WHY TRANSPOSE:
        # LIME uses (N, H, W, C)
        # PyTorch expects (N, C, H, W)
        images_tensor = torch.FloatTensor(images).permute(0, 3, 1, 2)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(images_tensor)
            probs = torch.softmax(outputs, dim=1)
        
        return probs.cpu().numpy()
    
    def explain_instance(
        self,
        image: np.ndarray,
        num_samples: int = 1000,
        num_features: int = 10,
        positive_only: bool = True
    ) -> Tuple[np.ndarray, dict]:
        """
        Explain a single prediction
        
        WHY THIS ALGORITHM:
            1. Segment image into superpixels
            2. Generate perturbed images (turn superpixels on/off)
            3. Get predictions for perturbed images
            4. Fit linear model to approximate behavior
            5. Return important superpixels
        
        WHY SUPERPIXELS:
            Pixel-level too fine-grained
            Superpixels are semantically meaningful
            Faster computation
        
        Args:
            image: Image to explain (H, W, C)
            num_samples: Number of perturbed samples
            num_features: Number of superpixels to highlight
            positive_only: Only show positive contributions
            
        Returns:
            Tuple of (explanation_image, explanation_dict)
        """
        logger.info(f"Explaining instance with {num_samples} samples")
        
        # Generate explanation
        # WHY THESE PARAMS:
        # top_labels: Explain top predicted classes
        # hide_color: Color for hidden superpixels (gray)
        # num_samples: More samples = better approximation but slower
        explanation = self.explainer.explain_instance(
            image,
            self.predict_fn,
            top_labels=2,
            hide_color=0,
            num_samples=num_samples
        )
        
        # Get explanation for top class
        # WHY TOP CLASS:
        # Most interested in why model made this prediction
        top_label = explanation.top_labels[0]
        
        # Get image and mask
        # WHY MASK:
        # Shows which superpixels are important
        # Can overlay on original image
        temp, mask = explanation.get_image_and_mask(
            top_label,
            positive_only=positive_only,
            num_features=num_features,
            hide_rest=False
        )
        
        # Create visualization
        # WHY MARK BOUNDARIES:
        # Shows which regions are important
        # Green boundaries = important regions
        explanation_image = mark_boundaries(temp / 255.0, mask)
        
        # Get feature importance
        # WHY FEATURE IMPORTANCE:
        # Quantify contribution of each superpixel
        # Can rank by importance
        feature_importance = dict(explanation.local_exp[top_label])
        
        explanation_dict = {
            'top_label': top_label,
            'feature_importance': feature_importance,
            'num_features': len(feature_importance)
        }
        
        logger.info(f"Generated explanation with {len(feature_importance)} features")
        
        return explanation_image, explanation_dict
    
    def compare_explanations(
        self,
        image1: np.ndarray,
        image2: np.ndarray,
        **kwargs
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compare explanations for two images
        
        WHY COMPARE:
            Understand what makes predictions different
            Useful for debugging model behavior
            Educational tool
        
        Args:
            image1: First image
            image2: Second image
            **kwargs: Arguments for explain_instance
            
        Returns:
            Tuple of (explanation1, explanation2)
        """
        exp1, _ = self.explain_instance(image1, **kwargs)
        exp2, _ = self.explain_instance(image2, **kwargs)
        
        return exp1, exp2


__all__ = ['LIMEExplainer']
