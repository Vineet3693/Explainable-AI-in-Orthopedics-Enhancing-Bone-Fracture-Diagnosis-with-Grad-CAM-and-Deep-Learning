"""
WHAT: Random Undersampling

WHY: Reduces majority class to balance dataset
     Simple and fast approach
     Creates balanced dataset

HOW:
     1. Count samples in each class
     2. Randomly remove samples from majority class
     3. Until both classes have equal samples

WHEN TO USE:
     ✅ Very large datasets (>100K samples)
     ✅ When training time is critical
     ✅ When you have redundant data

WHEN NOT TO USE:
     ❌ Small datasets (like FracAtlas - only 4K)
     ❌ When every sample is valuable
     ❌ Medical imaging (can't afford to lose data)

PROS:
     ✅ Simple to implement
     ✅ Fast training (less data)
     ✅ Balanced dataset
     ✅ No synthetic data

CONS:
     ⚠️ Loses valuable data
     ⚠️ May remove important examples
     ⚠️ Reduces model generalization
     ⚠️ Wastes collected data

EFFECT:
     - Majority class reduced
     - Balanced dataset
     - Faster training
     - BUT: Information loss

COMPARISON:
     vs Class Weights: Loses data, faster
     vs Focal Loss: Simpler but wasteful
     vs SMOTE: No synthetic data, but loses real data
     vs Oversampling: Opposite approach

MEDICAL AI WARNING:
     ⚠️ NOT RECOMMENDED for FracAtlas!
     - Only 4,083 images (small dataset)
     - Can't afford to lose 2,649 non-fractured images
     - Every X-ray is valuable medical data
     - Use Focal Loss + Class Weights instead

RECOMMENDATION FOR FRACATLAS:
     ❌ Don't use Undersampling
     ✅ Use Focal Loss + Class Weights
     
     Why: FracAtlas is small (4K images)
          Losing 65% of data is wasteful
          Better to use all data with proper weighting
"""

import numpy as np
from imblearn.under_sampling import RandomUnderSampler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UndersamplingBalancer:
    """
    Random Undersampling for data balancing
    
    WARNING: Not recommended for small datasets!
    Loses valuable data.
    
    For FracAtlas, use Focal Loss + Class Weights instead.
    """
    
    def __init__(self, random_state=42):
        """
        Initialize Random Undersampler
        
        Args:
            random_state: Random seed
        
        WARNING:
            This will remove majority class samples!
            Not suitable for small datasets like FracAtlas.
        """
        self.random_state = random_state
        self.undersampler = RandomUnderSampler(random_state=random_state)
        
        logger.warning("=" * 70)
        logger.warning("⚠️ UNDERSAMPLING INITIALIZED - NOT RECOMMENDED FOR FRACATLAS!")
        logger.warning("=" * 70)
        logger.warning("Undersampling removes majority class samples")
        logger.warning("FracAtlas only has 4,083 images - can't afford to lose data")
        logger.warning("This would remove 2,649 non-fractured images (65% of data!)")
        logger.warning("For FracAtlas, use Focal Loss + Class Weights instead")
        logger.warning("=" * 70)
    
    def balance_data(self, X, y):
        """
        Apply undersampling to balance data
        
        Args:
            X: Features
            y: Labels
        
        Returns:
            X_balanced, y_balanced
        
        WARNING:
            This removes majority class samples!
            Not suitable for small datasets!
        """
        logger.info("\n⚠️ Applying Undersampling (NOT RECOMMENDED)...")
        
        # Original distribution
        unique, counts = np.unique(y, return_counts=True)
        original_total = len(y)
        logger.info(f"Original distribution: {dict(zip(unique, counts))}")
        logger.info(f"Original total: {original_total} samples")
        
        # Apply undersampling
        X_balanced, y_balanced = self.undersampler.fit_resample(X, y)
        
        # New distribution
        unique, counts = np.unique(y_balanced, return_counts=True)
        new_total = len(y_balanced)
        removed = original_total - new_total
        
        logger.info(f"Balanced distribution: {dict(zip(unique, counts))}")
        logger.info(f"New total: {new_total} samples")
        logger.warning(f"⚠️ REMOVED {removed} samples ({removed/original_total*100:.1f}% of data)!")
        
        logger.warning("\n⚠️ WARNING: Valuable data has been discarded!")
        
        return X_balanced, y_balanced


def main():
    """
    Demonstration of why Undersampling is NOT recommended for FracAtlas
    """
    print("=" * 70)
    print("UNDERSAMPLING - WHY NOT TO USE FOR FRACATLAS")
    print("=" * 70)
    
    print("\n📊 FracAtlas Dataset:")
    print("  Total: 4,083 images")
    print("  Fractured: 717 (17.56%)")
    print("  Non-fractured: 3,366 (82.44%)")
    
    print("\n❌ What Undersampling would do:")
    print("  Keep: 717 fractured")
    print("  Keep: 717 non-fractured (randomly selected)")
    print("  REMOVE: 2,649 non-fractured images")
    print("  Result: 1,434 total images (65% data loss!)")
    
    print("\n❌ Problems:")
    print("  1. Loses 2,649 valuable X-ray images")
    print("  2. Reduces model generalization")
    print("  3. May remove important examples")
    print("  4. Wastes collected medical data")
    print("  5. Dataset becomes too small")
    
    print("\n✅ Better alternatives:")
    print("  1. Focal Loss (uses all data, weights loss)")
    print("  2. Class Weights (uses all data, weights samples)")
    print("  3. Both combined (recommended!)")
    
    print("\n💡 Recommendation for FracAtlas:")
    print("  Use: Focal Loss (α=0.75, γ=2.0) + Class Weights")
    print("  Don't use: Undersampling")
    print("  Reason: Dataset is small, can't afford to lose data")
    
    print("\n📚 When Undersampling is OK:")
    print("  - Very large datasets (>100K samples)")
    print("  - Redundant data")
    print("  - When training time is critical")
    
    print("\n" + "=" * 70)
    print("✅ For FracAtlas: Use recommended.py instead!")
    print("=" * 70)


if __name__ == "__main__":
    main()
