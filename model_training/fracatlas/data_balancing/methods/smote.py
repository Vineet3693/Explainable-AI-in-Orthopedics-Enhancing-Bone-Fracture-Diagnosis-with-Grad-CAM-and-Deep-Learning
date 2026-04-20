"""
WHAT: SMOTE - Synthetic Minority Over-sampling Technique

WHY: Creates synthetic samples for minority class
     Balances dataset at data level
     Popular technique for imbalanced data

HOW: 
     1. For each minority sample, find k nearest neighbors
     2. Randomly select one neighbor
     3. Create synthetic sample between them
     4. Repeat until balanced

WHEN TO USE:
     ✅ Tabular data (features, not images)
     ✅ Small datasets
     ✅ When you need more training samples

WHEN NOT TO USE:
     ❌ Medical images (like X-rays)
     ❌ Can create unrealistic samples
     ❌ Risk of overfitting on synthetic data

PROS:
     ✅ Creates new training samples
     ✅ Balances dataset
     ✅ Proven technique for tabular data

CONS:
     ⚠️ May create unrealistic X-rays
     ⚠️ Increases training time
     ⚠️ Risk of overfitting
     ⚠️ Not recommended for medical images

EFFECT:
     - Minority class gets synthetic samples
     - Dataset becomes balanced
     - Model sees more minority examples
     - BUT: Synthetic X-rays may not be realistic

COMPARISON:
     vs Class Weights: More complex, modifies data
     vs Focal Loss: Slower, changes data
     vs Undersampling: Doesn't lose data
     vs Oversampling: Creates new (not duplicate) samples

MEDICAL AI WARNING:
     ⚠️ NOT RECOMMENDED for FracAtlas!
     - Synthetic X-rays may not be medically valid
     - Could learn from unrealistic fractures
     - Use Focal Loss + Class Weights instead

RECOMMENDATION FOR FRACATLAS:
     ❌ Don't use SMOTE
     ✅ Use Focal Loss + Class Weights
     
     Why: X-ray images are complex medical data
          Synthetic interpolation may create invalid images
          Better to use loss-based balancing
"""

import numpy as np
from imblearn.over_sampling import SMOTE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMOTEBalancer:
    """
    SMOTE for data balancing
    
    WARNING: Not recommended for medical images!
    Use for educational purposes only.
    
    For FracAtlas, use Focal Loss + Class Weights instead.
    """
    
    def __init__(self, k_neighbors=5, random_state=42):
        """
        Initialize SMOTE
        
        Args:
            k_neighbors: Number of nearest neighbors
            random_state: Random seed
        
        WARNING:
            This is for demonstration only.
            Do NOT use on medical images!
        """
        self.k_neighbors = k_neighbors
        self.random_state = random_state
        self.smote = SMOTE(
            k_neighbors=k_neighbors,
            random_state=random_state
        )
        
        logger.warning("=" * 70)
        logger.warning("⚠️ SMOTE INITIALIZED - NOT RECOMMENDED FOR MEDICAL IMAGES!")
        logger.warning("=" * 70)
        logger.warning("SMOTE creates synthetic samples by interpolation")
        logger.warning("This may create unrealistic X-ray images")
        logger.warning("For FracAtlas, use Focal Loss + Class Weights instead")
        logger.warning("=" * 70)
    
    def balance_data(self, X, y):
        """
        Apply SMOTE to balance data
        
        Args:
            X: Features (flattened images)
            y: Labels
        
        Returns:
            X_balanced, y_balanced
        
        WARNING:
            This flattens images and creates synthetic samples
            Not suitable for medical imaging!
        """
        logger.info("\n⚠️ Applying SMOTE (NOT RECOMMENDED)...")
        
        # Original distribution
        unique, counts = np.unique(y, return_counts=True)
        logger.info(f"Original distribution: {dict(zip(unique, counts))}")
        
        # Apply SMOTE
        X_balanced, y_balanced = self.smote.fit_resample(X, y)
        
        # New distribution
        unique, counts = np.unique(y_balanced, return_counts=True)
        logger.info(f"Balanced distribution: {dict(zip(unique, counts))}")
        
        logger.warning("\n⚠️ WARNING: Synthetic samples may not be medically valid!")
        
        return X_balanced, y_balanced


def main():
    """
    Demonstration of why SMOTE is NOT recommended for medical images
    """
    print("=" * 70)
    print("SMOTE - WHY NOT TO USE FOR MEDICAL IMAGES")
    print("=" * 70)
    
    print("\n❌ Problems with SMOTE for X-rays:")
    print("  1. Creates synthetic images by interpolation")
    print("  2. Synthetic fractures may not be medically valid")
    print("  3. Model learns from unrealistic examples")
    print("  4. Risk of poor generalization")
    print("  5. Increases training time significantly")
    
    print("\n✅ Better alternatives:")
    print("  1. Focal Loss (handles imbalance in loss function)")
    print("  2. Class Weights (weights samples during training)")
    print("  3. Data Augmentation (rotation, zoom - realistic)")
    
    print("\n💡 Recommendation for FracAtlas:")
    print("  Use: Focal Loss (α=0.75, γ=2.0) + Class Weights")
    print("  Don't use: SMOTE")
    
    print("\n📚 When SMOTE is OK:")
    print("  - Tabular data (not images)")
    print("  - Non-medical applications")
    print("  - When synthetic samples are acceptable")
    
    print("\n" + "=" * 70)
    print("✅ For FracAtlas: Use recommended.py instead!")
    print("=" * 70)


if __name__ == "__main__":
    main()
