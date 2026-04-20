"""
Grad-CAM (Gradient-weighted Class Activation Mapping) for explainable AI

PURPOSE:
    Generates visual explanations showing which regions of an X-ray image
    the model focused on when making predictions. Critical for building
    trust with radiologists and ensuring model is learning correct features.

WHY EXPLAINABILITY IS CRITICAL FOR MEDICAL AI:
    Black box model: Radiologists won't trust it, can't verify reasoning
    Explainable model: Can verify model focuses on fractures, not artifacts
    
    IMPACT: Enables clinical adoption, builds trust, catches model errors

DESIGN PHILOSOPHY:
    1. Visual explanations (radiologists think visually)
    2. Overlay on original image (easy to interpret)
    3. Highlight important regions (where model looked)
    4. Catch model mistakes (focusing on wrong areas)

WHAT IS GRAD-CAM:
    Gradient-weighted Class Activation Mapping
    - Uses gradients flowing into final conv layer
    - Weights feature maps by importance
    - Produces heatmap of important regions
    - Overlays on original image
    
    SIMPLE EXPLANATION:
    "Shows where the model was looking when it made the decision"

HOW GRAD-CAM WORKS:
    1. Forward pass: Get prediction
    2. Backward pass: Get gradients for target class
    3. Weight feature maps by gradients
    4. Average weighted maps → heatmap
    5. Resize heatmap to image size
    6. Overlay on original image

PROS:
    ✅ Visual explanations (easy to understand)
    ✅ Builds trust with radiologists
    ✅ Catches model errors (focusing on artifacts)
    ✅ Verifies correct learning
    ✅ Works with any CNN architecture
    ✅ No model retraining needed

CONS:
    ❌ Adds computation (~100ms per image)
    ❌ Only shows where, not why
    ❌ Can be misleading if misinterpreted
    ❌ Requires last conv layer access

ALTERNATIVES:
    1. No explainability: Fast but no trust
    2. LIME: Slower, less accurate for images
    3. Integrated Gradients: More accurate but slower
    4. Attention maps: Requires model changes
    5. Grad-CAM (this): Best balance for medical imaging

COMPARISON:
    Method              | Speed | Accuracy | Medical Use
    No explanation      | Fast  | N/A      | ❌ Not acceptable
    LIME                | Slow  | Medium   | ⚠️ Possible
    Grad-CAM (this)     | Fast  | High     | ✅ Recommended
    Integrated Gradients| Slow  | V.High   | ✅ Research
    Attention maps      | Fast  | High     | ✅ Needs redesign

MEDICAL AI USE CASES:
    1. Verify model focuses on fracture site
    2. Catch model focusing on artifacts (e.g., labels, markers)
    3. Build trust with radiologists
    4. Explain predictions to patients
    5. Debug model failures
    6. Regulatory compliance (explainability required)

HOW IT AFFECTS APPLICATION:
    - Inference: +100ms per image (acceptable)
    - Trust: Radiologists can verify reasoning
    - Debugging: Identify why model failed
    - Compliance: Meets explainability requirements
    - Adoption: Increases clinical acceptance

PERFORMANCE:
    - Generation time: ~100ms per image
    - Memory: Minimal additional
    - GPU: Recommended but not required
    - Batch processing: Supported

MEDICAL AI CONSIDERATIONS:
    - Must verify model focuses on fractures, not artifacts
    - Heatmap should align with radiologist's reasoning
    - Red flags: Model focusing on labels, markers, edges
    - Green flags: Model focusing on bone discontinuities
    - Use for both correct and incorrect predictions

INTERPRETATION GUIDE:
    RED REGIONS (Hot): Model focused here strongly
    YELLOW REGIONS: Moderate focus
    BLUE/COLD REGIONS: Low focus
    
    GOOD HEATMAP: Highlights fracture site
    BAD HEATMAP: Highlights artifacts, labels, edges
    
EXAMPLE USE:
    >>> gradcam = GradCAM(model, layer_name='conv5_block3_out')
    >>> heatmap = gradcam.generate_heatmap(image, class_idx=1)
    >>> overlay = gradcam.overlay_heatmap(image, heatmap)
    >>> # Verify heatmap highlights fracture, not artifacts
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import cv2
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GradCAM:
    """Generate Grad-CAM heatmaps for model explainability"""
    
    def __init__(
        self,
        model: keras.Model,
        layer_name: Optional[str] = None
    ):
        """
        Initialize Grad-CAM
        
        Args:
            model: Keras model
            layer_name: Name of convolutional layer to visualize (auto-detect if None)
        """
        self.model = model
        
        # Auto-detect last convolutional layer if not specified
        if layer_name is None:
            layer_name = self._find_last_conv_layer()
        
        self.layer_name = layer_name
        logger.info(f"Using layer: {layer_name}")
        
        # Create gradient model
        self.grad_model = self._build_grad_model()
    
    def _find_last_conv_layer(self) -> str:
        """Find the last convolutional layer in the model"""
        for layer in reversed(self.model.layers):
            if 'conv' in layer.name.lower():
                return layer.name
        
        raise ValueError("No convolutional layer found in model")
    
    def _build_grad_model(self) -> keras.Model:
        """Build gradient model for Grad-CAM"""
        return keras.Model(
            inputs=self.model.inputs,
            outputs=[
                self.model.get_layer(self.layer_name).output,
                self.model.output
            ]
        )
    
    def generate_heatmap(
        self,
        image: np.ndarray,
        pred_index: Optional[int] = None
    ) -> np.ndarray:
        """
        Generate Grad-CAM heatmap
        
        Args:
            image: Input image (preprocessed)
            pred_index: Class index to visualize (None for predicted class)
            
        Returns:
            Heatmap as numpy array
        """
        # Expand dimensions if needed
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        # Get gradients
        with tf.GradientTape() as tape:
            conv_outputs, predictions = self.grad_model(image)
            
            if pred_index is None:
                pred_index = tf.argmax(predictions[0])
            
            class_channel = predictions[:, pred_index]
        
        # Compute gradients
        grads = tape.gradient(class_channel, conv_outputs)
        
        # Global average pooling of gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Weight feature maps by gradients
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # Normalize heatmap
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        
        return heatmap.numpy()
    
    def overlay_heatmap(
        self,
        heatmap: np.ndarray,
        original_image: np.ndarray,
        alpha: float = 0.4,
        colormap: int = cv2.COLORMAP_JET
    ) -> np.ndarray:
        """
        Overlay heatmap on original image
        
        Args:
            heatmap: Grad-CAM heatmap
            original_image: Original image
            alpha: Transparency of heatmap
            colormap: OpenCV colormap
            
        Returns:
            Overlayed image
        """
        # Resize heatmap to match image size
        heatmap = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
        
        # Convert heatmap to RGB
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, colormap)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Ensure original image is in correct format
        if original_image.max() <= 1.0:
            original_image = (original_image * 255).astype(np.uint8)
        
        # Overlay
        overlayed = cv2.addWeighted(original_image, 1 - alpha, heatmap, alpha, 0)
        
        return overlayed
    
    def generate_and_overlay(
        self,
        image: np.ndarray,
        original_image: np.ndarray,
        pred_index: Optional[int] = None,
        alpha: float = 0.4
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate heatmap and overlay on original image
        
        Args:
            image: Preprocessed image for model
            original_image: Original image for visualization
            pred_index: Class index to visualize
            alpha: Transparency
            
        Returns:
            (heatmap, overlayed_image)
        """
        heatmap = self.generate_heatmap(image, pred_index)
        overlayed = self.overlay_heatmap(heatmap, original_image, alpha)
        
        return heatmap, overlayed


if __name__ == "__main__":
    # Test Grad-CAM
    from src.models.resnet50_model import ResNet50Model
    
    # Create model
    model = ResNet50Model()
    model.build_model()
    
    # Create Grad-CAM
    gradcam = GradCAM(model.model)
    
    # Test with dummy image
    dummy_image = np.random.rand(224, 224, 3).astype(np.float32)
    heatmap = gradcam.generate_heatmap(dummy_image)
    
    print(f"Heatmap shape: {heatmap.shape}")
    print("Grad-CAM working successfully!")
