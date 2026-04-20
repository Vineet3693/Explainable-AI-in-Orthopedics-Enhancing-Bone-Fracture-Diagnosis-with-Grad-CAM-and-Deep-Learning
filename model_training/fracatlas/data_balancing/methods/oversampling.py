"""
WHAT: Random Oversampling

WHY: Duplicates minority class samples to balance dataset
     Simple approach to handle imbalance
     Creates balanced dataset

HOW:
     1. Count samples in each class
     2. Randomly duplicate minority class samples
     3. Until both classes have equal samples

WHEN TO USE:
     ✅ Quick experiments
     ✅ Baseline comparison
     ✅ When other methods aren't available

WHEN NOT TO USE:
     ❌ Production models (overfitting risk)
     ❌ When you need generalization
     ❌ Medical AI (exact duplicates don't add information)

PROS:
     ✅ Simple to implement
     ✅ No data loss
     ✅ Balanced dataset
     ✅ Fast to apply

CONS:
     ⚠️ Exact duplicates (no new information)
     ⚠️ Severe overfitting risk
     ⚠️ Longer training time
     ⚠️ Model memorizes duplicates

EFFECT:
     - Minority class duplicated
     - Balanced dataset
     - BUT: No new information added
     - High overfitting risk

COMPARISON:
     vs Class Weights: Simpler but less effective
     vs Focal Loss: Much less sophisticated
     vs SMOTE: No synthetic samples, just duplicates
     vs Undersampling: Opposite approach, keeps all data

MEDICAL AI WARNING:
     ⚠️ NOT RECOMMENDED for FracAtlas!
     - Exact duplicates don't help model learn
     - High risk of overfitting on duplicated fractures
     - Model may memorize instead of learning patterns
     - Use Focal Loss + Class Weights instead

RECOMMENDATION FOR FRACATLAS:
     ❌ Don't use Oversampling
     ✅ Use Focal Loss + Class Weights
     
     Why: Duplicates don't add information
          Better to use all data with proper weighting
          Focal Loss is more sophisticated
"""

import numpy as np
from imblearn.over_sampling import RandomOverSampler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OversamplingBalancer:
    """
    Random Oversampling for data balancing
    
    WARNING: Not recommended for production!
    Creates exact duplicates, high overfitting risk.
    
    For FracAtlas, use Focal Loss + Class Weights instead.
    """
    
    def __init__(self, random_state=42):
        """
        Initialize Random Oversampler
        
        Args:
            random_state: Random seed
        
        WARNING:
            This creates exact duplicates!
            High risk of overfitting.
        """
        self.random_state = random_state
        self.oversampler = RandomOverSampler(random_state=random_state)
        
        logger.warning("=" * 70)
        logger.warning("⚠️ OVERSAMPLING INITIALIZED - NOT RECOMMENDED FOR PRODUCTION!")
        logger.warning("=" * 70)
        logger.warning("Oversampling creates exact duplicates of minority class")
        logger.warning("This adds no new information, just repeats existing samples")
        logger.warning("High risk of overfitting - model may memorize duplicates")
        logger.warning("For FracAtlas, use Focal Loss + Class Weights instead")
        logger.warning("=" * 70)
    
    def balance_data(self, X, y):
        """
        Apply oversampling to balance data
        
        Args:
            X: Features
            y: Labels
        
        Returns:
            X_balanced, y_balanced
        
        WARNING:
            This creates exact duplicates!
            No new information added!
        """
        logger.info("\n⚠️ Applying Oversampling (NOT RECOMMENDED)...")
        
        # Original distribution
        unique, counts = np.unique(y, return_counts=True)
        original_total = len(y)
        logger.info(f"Original distribution: {dict(zip(unique, counts))}")
        logger.info(f"Original total: {original_total} samples")
        
        # Apply oversampling
        X_balanced, y_balanced = self.oversampler.fit_resample(X, y)
        
        # New distribution
        unique, counts = np.unique(y_balanced, return_counts=True)
        new_total = len(y_balanced)
        added = new_total - original_total
        
        logger.info(f"Balanced distribution: {dict(zip(unique, counts))}")
        logger.info(f"New total: {new_total} samples")
        logger.warning(f"⚠️ ADDED {added} duplicate samples ({added/original_total*100:.1f}% increase)!")
        
        logger.warning("\n⚠️ WARNING: These are exact duplicates, no new information!")
        
        return X_balanced, y_balanced


def main():
    """
    Demonstration of why Oversampling is NOT recommended for FracAtlas
    """
    print("=" * 70)
    print("OVERSAMPLING - WHY NOT TO USE FOR FRACATLAS")
    print("=" * 70)
    
    print("\n📊 FracAtlas Dataset:")
    print("  Total: 4,083 images")
    print("  Fractured: 717 (17.56%)")
    print("  Non-fractured: 3,366 (82.44%)")
    
    print("\n❌ What Oversampling would do:")
    print("  Keep: 3,366 non-fractured (original)")
    print("  Keep: 717 fractured (original)")
    print("  ADD: 2,649 fractured (DUPLICATES)")
    print("  Result: 7,032 total images (but 2,649 are duplicates!)")
    
    print("\n❌ Problems:")
    print("  1. Creates 2,649 exact duplicate X-rays")
    print("  2. No new information added")
    print("  3. Model may memorize duplicates")
    print("  4. High overfitting risk")
    print("  5. Longer training time for no benefit")
    
    print("\n✅ Better alternatives:")
    print("  1. Focal Loss (smart weighting, no duplicates)")
    print("  2. Class Weights (weights samples, no duplicates)")
    print("  3. Data Augmentation (creates variations, not duplicates)")
    
    print("\n💡 Recommendation for FracAtlas:")
    print("  Use: Focal Loss (α=0.75, γ=2.0) + Class Weights")
    print("  Don't use: Oversampling")
    print("  Reason: Duplicates don't help, focal loss is smarter")
    
    print("\n📚 When Oversampling might be OK:")
    print("  - Quick baseline experiments")
    print("  - Comparing with other methods")
    print("  - Never for production!")
    
    print("\n" + "=" * 70)
    print("✅ For FracAtlas: Use recommended.py instead!")
    print("=" * 70)


if __name__ == "__main__":
    main()
