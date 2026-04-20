"""
Integrated Gradients for Model Explainability

PURPOSE:
    Implements Integrated Gradients attribution method for explaining CNN predictions.
    Shows which parts of X-ray image contributed to fracture detection.

WHY INTEGRATED GRADIENTS:
    Grad-CAM: Only shows last layer, may miss details
    Integrated Gradients (this): Theoretically grounded, pixel-level attribution
    
    IMPACT: Better explanations, increased trust

DESIGN PHILOSOPHY:
    1. Theoretically sound (satisfies axioms)
    2. Pixel-level attribution (fine-grained)
    3. Model-agnostic (works with any differentiable model)
    4. Baseline comparison (what changed from baseline)

PROS:
    ✅ Theoretically grounded (satisfies completeness axiom)
    ✅ Pixel-level attribution
    ✅ Works with any differentiable model
    ✅ No model modification needed

CONS:
    ❌ Computationally expensive (many forward passes)
    ❌ Requires choosing baseline image
    ❌ Can be noisy
    ❌ Harder to interpret than Grad-CAM

ALTERNATIVES:
    1. Grad-CAM: Faster but coarser
    2. LIME: Model-agnostic but slower
    3. SHAP: Theoretically sound but very slow
    4. Integrated Gradients (this): Balance of theory and speed

COMPARISON:
    | Method              | Speed | Granularity | Theory | Interpretability |
    |---------------------|-------|-------------|--------|------------------|
    | Grad-CAM            | ✅    | Coarse      | ⚠️     | ✅               |
    | LIME                | ❌    | Medium      | ⚠️     | ✅               |
    | SHAP                | ❌    | Fine        | ✅     | ⚠️               |
    | Integrated Gradients| ⚠️    | Fine        | ✅     | ⚠️               |

USAGE:
    from src.explainability.integrated_gradients import IntegratedGradients
    
    ig = IntegratedGradients(model)
    attributions = ig.attribute(
        image,
        target_class=1,  # Fracture
        n_steps=50
    )
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class IntegratedGradients:
    """
    Integrated Gradients attribution method
    
    WHY INTEGRATED GRADIENTS:
        Satisfies completeness axiom:
        sum(attributions) = output - baseline_output
        
        This means attributions fully explain the prediction
    """
    
    def __init__(self, model: nn.Module):
        """
        Initialize Integrated Gradients
        
        Args:
            model: PyTorch model to explain
        """
        self.model = model
        self.model.eval()  # WHY EVAL: No dropout/batch norm randomness
        
        logger.info("Initialized IntegratedGradients")
    
    def attribute(
        self,
        image: torch.Tensor,
        target_class: int,
        baseline: Optional[torch.Tensor] = None,
        n_steps: int = 50
    ) -> np.ndarray:
        """
        Compute integrated gradients attribution
        
        WHY THIS ALGORITHM:
            1. Create path from baseline to input
            2. Compute gradients along path
            3. Integrate (sum) gradients
            4. Scale by (input - baseline)
        
        FORMULA:
            IG(x) = (x - x') * ∫[0,1] ∂F(x' + α(x - x'))/∂x dα
            
        WHERE:
            x: input image
            x': baseline image
            F: model output
            α: interpolation coefficient
        
        Args:
            image: Input image tensor (1, C, H, W)
            target_class: Class to explain (0 or 1)
            baseline: Baseline image (default: black image)
            n_steps: Number of integration steps
            
        Returns:
            Attribution map (H, W)
        """
        # WHY BASELINE:
        # Need reference point for comparison
        # Black image = "no information"
        # Attributions show what changed from baseline
        if baseline is None:
            baseline = torch.zeros_like(image)
        
        # WHY REQUIRE GRAD:
        # Need to compute gradients w.r.t. input
        image.requires_grad = True
        
        # Create interpolated images
        # WHY INTERPOLATE:
        # Create smooth path from baseline to input
        # Integrate gradients along this path
        alphas = torch.linspace(0, 1, n_steps)
        
        # Store gradients
        gradients = []
        
        for alpha in alphas:
            # Interpolated image
            # WHY THIS FORMULA:
            # α=0: baseline
            # α=1: input
            # α=0.5: halfway between
            interpolated = baseline + alpha * (image - baseline)
            interpolated.requires_grad = True
            
            # Forward pass
            output = self.model(interpolated)
            
            # Get output for target class
            # WHY TARGET CLASS:
            # Explain why model predicted this class
            # Not other classes
            target_output = output[0, target_class]
            
            # Backward pass
            # WHY BACKWARD:
            # Compute ∂output/∂input
            # Shows how input affects output
            self.model.zero_grad()
            target_output.backward()
            
            # Store gradient
            gradients.append(interpolated.grad.detach().cpu().numpy())
        
        # Average gradients
        # WHY AVERAGE:
        # Approximate integral by averaging
        # Riemann sum approximation
        avg_gradients = np.mean(gradients, axis=0)
        
        # Integrated gradients
        # WHY MULTIPLY:
        # Scale by (input - baseline)
        # Completes the integration formula
        integrated_grads = (image - baseline).detach().cpu().numpy() * avg_gradients
        
        # Sum across channels
        # WHY SUM CHANNELS:
        # Get single attribution map
        # Easier to visualize
        attribution = np.sum(integrated_grads[0], axis=0)
        
        logger.info(f"Computed integrated gradients with {n_steps} steps")
        
        return attribution
    
    def visualize_attribution(
        self,
        image: np.ndarray,
        attribution: np.ndarray,
        percentile: float = 99
    ) -> np.ndarray:
        """
        Create visualization of attribution
        
        WHY VISUALIZE:
            Raw attributions are hard to interpret
            Overlay on image shows what model "sees"
            
        Args:
            image: Original image (H, W) or (H, W, C)
            attribution: Attribution map (H, W)
            percentile: Percentile for normalization
            
        Returns:
            Visualization (H, W, 3)
        """
        import cv2
        
        # Normalize attribution
        # WHY PERCENTILE:
        # Outliers can dominate color scale
        # Percentile clipping improves visualization
        vmax = np.percentile(np.abs(attribution), percentile)
        attribution_norm = np.clip(attribution / vmax, -1, 1)
        
        # Create heatmap
        # WHY HEATMAP:
        # Color shows attribution strength
        # Red = positive (supports prediction)
        # Blue = negative (opposes prediction)
        heatmap = cv2.applyColorMap(
            np.uint8(255 * (attribution_norm + 1) / 2),
            cv2.COLORMAP_JET
        )
        
        # Overlay on image
        # WHY OVERLAY:
        # Shows attribution in context
        # Easier to understand than heatmap alone
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        overlay = cv2.addWeighted(image, 0.6, heatmap, 0.4, 0)
        
        return overlay


__all__ = ['IntegratedGradients']
