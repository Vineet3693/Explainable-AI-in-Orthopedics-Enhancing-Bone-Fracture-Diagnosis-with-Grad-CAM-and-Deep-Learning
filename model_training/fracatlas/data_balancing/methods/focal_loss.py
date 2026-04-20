"""
WHAT: Focal Loss - Advanced Loss Function for Imbalanced Data

WHY: Standard loss treats all examples equally
     Focal Loss focuses on hard-to-classify examples
     Reduces weight of easy examples, increases weight of hard examples
     Specifically designed for class imbalance

HOW: FL(p_t) = -α(1-p_t)^γ * log(p_t)
     where:
     - p_t = predicted probability for true class
     - α (alpha) = weight for positive class (0-1)
     - γ (gamma) = focusing parameter (0-5)
     
     Higher γ = more focus on hard examples

WHEN TO USE:
    ✅ Highly imbalanced datasets (like FracAtlas)
    ✅ When many easy examples dominate training
    ✅ Medical AI (missing positive case is critical)
    ✅ When class weights alone aren't enough

PROS:
    ✅ Handles extreme imbalance (1:100 or worse)
    ✅ Focuses on hard examples automatically
    ✅ Reduces overfitting on easy examples
    ✅ Better than class weights for hard cases
    ✅ Industry standard for medical imaging

CONS:
    ⚠️ Requires tuning (α and γ parameters)
    ⚠️ Slightly slower than binary crossentropy
    ⚠️ Can be unstable with wrong parameters
    ⚠️ More complex to understand

EFFECT:
    - Easy examples (p_t > 0.9): Very low loss
    - Hard examples (p_t < 0.5): High loss
    - Model focuses learning on difficult cases
    - Improves recall on minority class

COMPARISON:
    vs Binary Crossentropy: Much better for imbalanced data
    vs Class Weights: More sophisticated, handles hard examples
    vs SMOTE: No data modification needed
    vs Weighted BCE: Focal loss is superior

MEDICAL AI IMPACT:
    Critical for fracture detection!
    - Focuses on hard-to-detect fractures
    - Reduces false negatives
    - Improves sensitivity (recall)
    - Standard in medical imaging papers

PARAMETERS:
    α (alpha): 0.25-0.75 for minority class
               Higher α = more weight on minority class
               FracAtlas: Use 0.75 (minority is 17%)
    
    γ (gamma): 0-5, typically 2.0
               Higher γ = more focus on hard examples
               FracAtlas: Use 2.0 (standard)

EXAMPLE VALUES:
    Easy example (p_t=0.95, α=0.75, γ=2):
        FL = -0.75 × (1-0.95)^2 × log(0.95)
        FL = -0.75 × 0.0025 × 0.051 = 0.0001
        → Almost zero loss (ignored)
    
    Hard example (p_t=0.3, α=0.75, γ=2):
        FL = -0.75 × (1-0.3)^2 × log(0.3)
        FL = -0.75 × 0.49 × 1.204 = 0.442
        → High loss (focused on)
"""

import tensorflow as tf
import numpy as np
from typing import Callable, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FocalLoss:
    """
    Focal Loss for handling imbalanced classification
    
    PURPOSE:
        Down-weight easy examples, focus on hard examples
        Automatically handles class imbalance
    
    ALGORITHM:
        For each example:
        1. Get predicted probability p_t for true class
        2. Calculate modulating factor: (1 - p_t)^γ
        3. Apply class weight: α
        4. Compute: FL = -α(1-p_t)^γ × log(p_t)
    
    INTUITION:
        - If model is confident and correct (p_t=0.99):
          → (1-0.99)^2 = 0.0001 → loss ≈ 0 → ignored
        
        - If model is uncertain (p_t=0.6):
          → (1-0.6)^2 = 0.16 → moderate loss → learned
        
        - If model is wrong (p_t=0.1):
          → (1-0.1)^2 = 0.81 → high loss → focused on
    
    MEDICAL AI CONTEXT:
        In fracture detection:
        - Easy cases: Clear fractures, obvious normal X-rays
        - Hard cases: Hairline fractures, subtle abnormalities
        
        Focal loss ensures model learns to detect subtle fractures
        instead of just memorizing obvious cases
    """
    
    def __init__(self, alpha: float = 0.75, gamma: float = 2.0):
        """
        Initialize Focal Loss
        
        Args:
            alpha: Weight for positive class (fractured)
                   Range: 0-1
                   FracAtlas: 0.75 (minority is 17%, so high weight)
                   
            gamma: Focusing parameter
                   Range: 0-5
                   0 = no focusing (same as BCE)
                   2 = standard (recommended)
                   5 = extreme focusing
        
        WHY THESE DEFAULTS:
            α=0.75: FracAtlas has 17% positive class
                    High α compensates for imbalance
            
            γ=2.0: Standard value from original paper
                   Proven to work well across datasets
        
        TUNING GUIDE:
            If recall is low: Increase α (0.75 → 0.85)
            If overfitting on minority: Decrease α (0.75 → 0.65)
            If not learning hard cases: Increase γ (2.0 → 3.0)
            If unstable training: Decrease γ (2.0 → 1.0)
        """
        self.alpha = alpha
        self.gamma = gamma
        
        logger.info("=" * 60)
        logger.info("FOCAL LOSS INITIALIZED")
        logger.info("=" * 60)
        logger.info(f"Alpha (α): {alpha}")
        logger.info(f"  → Positive class weight: {alpha:.2f}")
        logger.info(f"  → Negative class weight: {1-alpha:.2f}")
        logger.info(f"\nGamma (γ): {gamma}")
        logger.info(f"  → Focusing strength: {'Low' if gamma < 1.5 else 'Medium' if gamma < 3 else 'High'}")
        logger.info("=" * 60)
    
    def __call__(self, y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
        """
        Calculate focal loss
        
        Args:
            y_true: True labels (0 or 1)
            y_pred: Predicted probabilities (0-1)
        
        Returns:
            Focal loss value
        
        STEP-BY-STEP:
            1. Clip predictions to avoid log(0)
            2. Calculate binary cross entropy
            3. Calculate modulating factor (1-p_t)^γ
            4. Apply class weight α
            5. Combine all components
        
        MATHEMATICAL BREAKDOWN:
            BCE = -y_true×log(y_pred) - (1-y_true)×log(1-y_pred)
            p_t = y_true×y_pred + (1-y_true)×(1-y_pred)
            modulating = (1 - p_t)^γ
            weight = α×y_true + (1-α)×(1-y_true)
            FL = weight × modulating × BCE
        """
        # Clip predictions to prevent log(0)
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
        
        # Calculate binary cross entropy
        # BCE = -[y×log(p) + (1-y)×log(1-p)]
        cross_entropy = -y_true * tf.math.log(y_pred) - (1 - y_true) * tf.math.log(1 - y_pred)
        
        # Calculate p_t (probability of true class)
        # If y=1: p_t = p
        # If y=0: p_t = 1-p
        p_t = y_true * y_pred + (1 - y_true) * (1 - y_pred)
        
        # Calculate modulating factor: (1 - p_t)^γ
        # This is the KEY component of focal loss
        # Easy examples (p_t ≈ 1): factor ≈ 0 → loss ≈ 0
        # Hard examples (p_t ≈ 0): factor ≈ 1 → loss = full BCE
        modulating_factor = tf.pow(1 - p_t, self.gamma)
        
        # Calculate class weight
        # Positive class (y=1): weight = α
        # Negative class (y=0): weight = 1-α
        alpha_weight = self.alpha * y_true + (1 - self.alpha) * (1 - y_true)
        
        # Combine all components
        focal_loss = alpha_weight * modulating_factor * cross_entropy
        
        return tf.reduce_mean(focal_loss)
    
    def get_loss_function(self) -> Callable:
        """
        Get focal loss as a Keras-compatible function
        
        Returns:
            Loss function for model.compile()
        
        USAGE:
            focal = FocalLoss(alpha=0.75, gamma=2.0)
            model.compile(loss=focal.get_loss_function(), ...)
        """
        return self.__call__
    
    def analyze_example(self, y_true: float, y_pred: float) -> dict:
        """
        Analyze focal loss for a single example
        
        Args:
            y_true: True label (0 or 1)
            y_pred: Predicted probability (0-1)
        
        Returns:
            Detailed breakdown of loss calculation
        
        PURPOSE:
            Understand how focal loss treats different examples
        
        EXAMPLE:
            focal = FocalLoss(alpha=0.75, gamma=2.0)
            focal.analyze_example(y_true=1, y_pred=0.95)  # Easy positive
            focal.analyze_example(y_true=1, y_pred=0.3)   # Hard positive
        """
        # Calculate components
        epsilon = 1e-7
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        
        # Binary cross entropy
        bce = -(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        
        # p_t (probability of true class)
        p_t = y_true * y_pred + (1 - y_true) * (1 - y_pred)
        
        # Modulating factor
        modulating = (1 - p_t) ** self.gamma
        
        # Alpha weight
        alpha_weight = self.alpha if y_true == 1 else (1 - self.alpha)
        
        # Focal loss
        fl = alpha_weight * modulating * bce
        
        # Classification
        difficulty = "Easy" if p_t > 0.8 else "Medium" if p_t > 0.5 else "Hard"
        
        return {
            'true_label': int(y_true),
            'predicted_prob': y_pred,
            'p_t': p_t,
            'difficulty': difficulty,
            'bce': bce,
            'modulating_factor': modulating,
            'alpha_weight': alpha_weight,
            'focal_loss': fl,
            'reduction_vs_bce': f"{(1 - fl/bce) * 100:.1f}%" if bce > 0 else "N/A"
        }


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_basic_usage():
    """
    EXAMPLE 1: Basic focal loss usage
    
    DEMONSTRATES:
        How to create and use focal loss
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Focal Loss Usage")
    print("=" * 60)
    
    # Create focal loss
    focal = FocalLoss(alpha=0.75, gamma=2.0)
    
    # Example predictions
    y_true = tf.constant([[1.0], [0.0], [1.0], [0.0]])
    y_pred = tf.constant([[0.9], [0.1], [0.3], [0.8]])
    
    # Calculate loss
    loss = focal(y_true, y_pred)
    
    print(f"\nLoss value: {loss.numpy():.4f}")
    
    return focal


def example_comparison_with_bce():
    """
    EXAMPLE 2: Compare focal loss with binary crossentropy
    
    SHOWS:
        How focal loss down-weights easy examples
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Focal Loss vs Binary Crossentropy")
    print("=" * 60)
    
    focal = FocalLoss(alpha=0.75, gamma=2.0)
    
    # Test cases
    test_cases = [
        (1, 0.95, "Easy positive (confident, correct)"),
        (1, 0.6, "Medium positive (uncertain)"),
        (1, 0.2, "Hard positive (confident, wrong)"),
        (0, 0.05, "Easy negative (confident, correct)"),
        (0, 0.4, "Medium negative (uncertain)"),
        (0, 0.8, "Hard negative (confident, wrong)")
    ]
    
    print(f"\n{'Case':<40} {'BCE':<10} {'Focal':<10} {'Reduction':<12}")
    print("-" * 75)
    
    for y_true, y_pred, description in test_cases:
        analysis = focal.analyze_example(y_true, y_pred)
        
        print(f"{description:<40} "
              f"{analysis['bce']:<10.4f} "
              f"{analysis['focal_loss']:<10.4f} "
              f"{analysis['reduction_vs_bce']:<12}")
    
    print("\n💡 Key Insight:")
    print("  Easy examples: Focal loss << BCE (down-weighted)")
    print("  Hard examples: Focal loss ≈ BCE (full weight)")


def example_parameter_tuning():
    """
    EXAMPLE 3: Effect of different parameters
    
    DEMONSTRATES:
        How α and γ affect the loss
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Parameter Tuning")
    print("=" * 60)
    
    # Test case: Hard positive example
    y_true, y_pred = 1, 0.3
    
    print(f"\nTest case: True={y_true}, Pred={y_pred} (Hard positive)")
    print(f"\n{'Alpha':<8} {'Gamma':<8} {'Loss':<10} {'Effect':<30}")
    print("-" * 60)
    
    # Test different parameters
    params = [
        (0.25, 2.0, "Low α: Less weight on positive"),
        (0.75, 2.0, "High α: More weight on positive"),
        (0.75, 0.0, "γ=0: No focusing (= BCE)"),
        (0.75, 1.0, "γ=1: Light focusing"),
        (0.75, 2.0, "γ=2: Standard focusing"),
        (0.75, 5.0, "γ=5: Extreme focusing"),
    ]
    
    for alpha, gamma, description in params:
        focal = FocalLoss(alpha=alpha, gamma=gamma)
        analysis = focal.analyze_example(y_true, y_pred)
        
        print(f"{alpha:<8.2f} {gamma:<8.1f} {analysis['focal_loss']:<10.4f} {description:<30}")
    
    print("\n💡 Tuning Guide:")
    print("  ↑ α → More weight on minority class")
    print("  ↑ γ → More focus on hard examples")


def example_medical_ai_context():
    """
    EXAMPLE 4: Medical AI context
    
    EXPLAINS:
        Why focal loss is critical for fracture detection
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Medical AI Context")
    print("=" * 60)
    
    focal = FocalLoss(alpha=0.75, gamma=2.0)
    
    print("\n🏥 Fracture Detection Scenarios:")
    print("\n1. OBVIOUS FRACTURE (Easy Positive):")
    print("   X-ray: Clear bone break, displaced fragments")
    analysis1 = focal.analyze_example(y_true=1, y_pred=0.98)
    print(f"   Model confidence: {analysis1['predicted_prob']:.2f}")
    print(f"   Focal loss: {analysis1['focal_loss']:.4f} (very low)")
    print(f"   → Model already learned this, move on")
    
    print("\n2. HAIRLINE FRACTURE (Hard Positive):")
    print("   X-ray: Subtle crack, hard to see")
    analysis2 = focal.analyze_example(y_true=1, y_pred=0.4)
    print(f"   Model confidence: {analysis2['predicted_prob']:.2f}")
    print(f"   Focal loss: {analysis2['focal_loss']:.4f} (high)")
    print(f"   → Model needs to learn this, focus here!")
    
    print("\n3. NORMAL X-RAY (Easy Negative):")
    print("   X-ray: Perfectly healthy bone")
    analysis3 = focal.analyze_example(y_true=0, y_pred=0.02)
    print(f"   Model confidence: {1-analysis3['predicted_prob']:.2f}")
    print(f"   Focal loss: {analysis3['focal_loss']:.4f} (very low)")
    print(f"   → Model already learned this, move on")
    
    print("\n💡 Medical AI Benefit:")
    print("  Focal loss ensures model learns to detect")
    print("  subtle fractures, not just obvious ones!")
    print("  Critical for patient safety!")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Demonstrate all features of Focal Loss
    """
    print("=" * 60)
    print("FOCAL LOSS - COMPLETE DEMONSTRATION")
    print("=" * 60)
    
    # Run examples
    example_basic_usage()
    example_comparison_with_bce()
    example_parameter_tuning()
    example_medical_ai_context()
    
    print("\n" + "=" * 60)
    print("✅ FOCAL LOSS DEMONSTRATION COMPLETE")
    print("=" * 60)
    
    print("\n📚 KEY TAKEAWAYS:")
    print("  1. Focal loss focuses on hard examples")
    print("  2. Down-weights easy examples automatically")
    print("  3. Critical for imbalanced medical data")
    print("  4. α controls class balance, γ controls focusing")
    print("  5. Standard: α=0.75, γ=2.0 for FracAtlas")
    print("  6. Combine with class weights for best results")


if __name__ == "__main__":
    main()
