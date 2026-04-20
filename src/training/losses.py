"""
Custom Loss Functions for Medical AI

PURPOSE:
    Implements specialized loss functions for medical image classification.
    Addresses class imbalance and prioritizes sensitivity over accuracy.

WHY CUSTOM LOSSES:
    Standard cross-entropy: Treats all errors equally
    Medical AI (this): Penalizes false negatives more heavily
    
    IMPACT: Better fracture detection, fewer missed cases

DESIGN PHILOSOPHY:
    1. Safety-first (penalize false negatives heavily)
    2. Class imbalance handling (weighted/focal loss)
    3. Interpretability (understand what model optimizes)
    4. Flexibility (configurable weights)

PROS:
    ✅ Addresses class imbalance
    ✅ Prioritizes patient safety (high sensitivity)
    ✅ Proven in medical AI literature
    ✅ Configurable for different use cases

CONS:
    ❌ More complex than standard loss
    ❌ Requires tuning hyperparameters
    ❌ Can overfit if not careful

ALTERNATIVES:
    1. Standard cross-entropy: Simple but ignores imbalance
    2. Weighted cross-entropy: Good but less sophisticated
    3. Focal loss (this): Best for hard examples
    4. Dice loss: Better for segmentation, not classification
    
COMPARISON:
    | Loss Function      | Imbalance | Hard Examples | Medical AI | Complexity |
    |--------------------|-----------|---------------|------------|------------|
    | Cross-Entropy      | ❌        | ❌            | ❌         | Low        |
    | Weighted CE        | ✅        | ❌            | ⚠️         | Medium     |
    | Focal Loss         | ✅        | ✅            | ✅         | Medium     |
    | Custom Weighted    | ✅        | ⚠️            | ✅         | Medium     |

USAGE:
    from src.training.losses import FocalLoss, WeightedBinaryCrossEntropy
    
    # Focal loss (recommended)
    loss_fn = FocalLoss(alpha=0.25, gamma=2.0)
    
    # Weighted loss
    loss_fn = WeightedBinaryCrossEntropy(
        false_negative_weight=5.0,  # Penalize FN heavily
        false_positive_weight=1.0
    )
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FocalLoss(nn.Module):
    """
    Focal Loss for addressing class imbalance
    
    WHY FOCAL LOSS:
        Focuses on hard-to-classify examples
        Reduces weight of easy examples
        Proven effective for medical imaging
    
    FORMULA:
        FL(p_t) = -α_t * (1 - p_t)^γ * log(p_t)
        
    WHERE:
        p_t: predicted probability of correct class
        α_t: class weight (balances positive/negative)
        γ: focusing parameter (reduces easy example weight)
    
    WHY THESE PARAMETERS:
        α (alpha): Balances class frequencies
        γ (gamma): Controls focus on hard examples
            - γ=0: Standard cross-entropy
            - γ=2: Recommended default (from paper)
            - γ>2: More focus on hard examples
    """
    
    def __init__(
        self,
        alpha: float = 0.25,
        gamma: float = 2.0,
        reduction: str = 'mean'
    ):
        """
        Initialize Focal Loss
        
        Args:
            alpha: Weight for positive class (0.0-1.0)
            gamma: Focusing parameter (typically 2.0)
            reduction: 'none', 'mean', or 'sum'
        """
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        
        # WHY LOG THESE:
        # Important for debugging and reproducibility
        # Know exactly what loss function was used
        logger.info(f"Initialized FocalLoss(alpha={alpha}, gamma={gamma})")
    
    def forward(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute focal loss
        
        WHY THIS IMPLEMENTATION:
            Numerically stable (uses log_softmax)
            Handles edge cases (clipping)
            Efficient (vectorized operations)
        
        Args:
            inputs: Model predictions (logits)
            targets: Ground truth labels
            
        Returns:
            Focal loss value
        """
        # WHY SIGMOID:
        # Convert logits to probabilities
        # Ensures values in [0, 1] range
        probs = torch.sigmoid(inputs)
        
        # WHY CLAMP:
        # Prevent log(0) = -inf
        # Numerical stability
        probs = torch.clamp(probs, min=1e-7, max=1-1e-7)
        
        # Compute focal loss components
        # WHY SEPARATE POSITIVE/NEGATIVE:
        # Different weights for each class
        # Handles class imbalance
        pos_loss = -self.alpha * (1 - probs) ** self.gamma * torch.log(probs)
        neg_loss = -(1 - self.alpha) * probs ** self.gamma * torch.log(1 - probs)
        
        # Combine based on targets
        loss = targets * pos_loss + (1 - targets) * neg_loss
        
        # Apply reduction
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss


class WeightedBinaryCrossEntropy(nn.Module):
    """
    Weighted Binary Cross-Entropy Loss
    
    WHY WEIGHTED:
        Penalize false negatives more than false positives
        Critical for medical AI safety
        Simple and interpretable
    
    WHEN TO USE:
        - Class imbalance exists
        - False negatives are more dangerous
        - Need interpretable loss function
    """
    
    def __init__(
        self,
        false_negative_weight: float = 5.0,
        false_positive_weight: float = 1.0
    ):
        """
        Initialize weighted loss
        
        WHY THESE WEIGHTS:
            FN weight = 5.0: Missing fracture is 5x worse than false alarm
            FP weight = 1.0: False alarm is still bad but less critical
            
        Args:
            false_negative_weight: Penalty for missing fractures
            false_positive_weight: Penalty for false alarms
        """
        super(WeightedBinaryCrossEntropy, self).__init__()
        self.fn_weight = false_negative_weight
        self.fp_weight = false_positive_weight
        
        logger.info(
            f"Initialized WeightedBCE(FN_weight={false_negative_weight}, "
            f"FP_weight={false_positive_weight})"
        )
    
    def forward(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute weighted binary cross-entropy
        
        Args:
            inputs: Model predictions (logits)
            targets: Ground truth labels (0 or 1)
            
        Returns:
            Weighted loss value
        """
        # WHY SIGMOID:
        # Convert logits to probabilities
        probs = torch.sigmoid(inputs)
        
        # WHY CLAMP:
        # Numerical stability
        probs = torch.clamp(probs, min=1e-7, max=1-1e-7)
        
        # Compute weighted loss
        # WHY SEPARATE TERMS:
        # Different weights for positive and negative examples
        # Positive (fracture): weight by fn_weight
        # Negative (normal): weight by fp_weight
        pos_loss = -self.fn_weight * targets * torch.log(probs)
        neg_loss = -self.fp_weight * (1 - targets) * torch.log(1 - probs)
        
        loss = pos_loss + neg_loss
        
        return loss.mean()


__all__ = [
    'FocalLoss',
    'WeightedBinaryCrossEntropy'
]
