"""
Base model class for transfer learning architectures

PURPOSE:
    Provides abstract base class for all CNN models, ensuring consistent
    interface and reducing code duplication. Implements common functionality
    shared across ResNet50, VGG16, and EfficientNet.

DESIGN PATTERN:
    Template Method Pattern - defines skeleton of algorithm, subclasses
    implement specific steps (build_model)

WHY ABSTRACT BASE CLASS:
    ✅ Enforces consistent interface across models
    ✅ Reduces code duplication (DRY principle)
    ✅ Easy to add new model architectures
    ✅ Centralized compilation and training logic
    ✅ Type safety with ABC

PROS:
    ✅ Consistent API for all models
    ✅ Shared functionality (compile, summary, save)
    ✅ Easy model swapping (just change class)
    ✅ Enforces implementation of required methods

CONS:
    ❌ Slight overhead from abstraction
    ❌ May be over-engineering for simple projects
    ❌ Requires understanding of inheritance

ALTERNATIVES:
    1. Separate classes without inheritance: More duplication
    2. Factory functions: Less structure, harder to extend
    3. Composition over inheritance: More flexible but complex
    4. Protocol/Interface (typing.Protocol): Python 3.8+ only

HOW IT AFFECTS APPLICATION:
    - Enables easy model comparison (swap one line)
    - Ensures all models have same interface
    - Reduces bugs from inconsistent implementations
    - Makes codebase more maintainable
"""

from abc import ABC, abstractmethod
from tensorflow import keras
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for transfer learning models
    
    ARCHITECTURE PATTERN:
        All models follow this structure:
        
        Input (224x224x3)
        ↓
        Pre-trained Base (ImageNet weights)
        ↓
        Custom Classification Head
        ↓
        Output (1 for binary, N for multi-class)
    
    INHERITANCE HIERARCHY:
        BaseModel (abstract)
        ├── ResNet50Model
        ├── VGG16Model
        └── EfficientNetModel
    
    REQUIRED METHODS:
        Subclasses MUST implement:
        - build_model(): Construct the model architecture
    
    PROVIDED METHODS:
        Subclasses inherit:
        - compile_model(): Compile with optimizer and loss
        - summary(): Print model architecture
        - save(): Save model to disk
        - load(): Load model from disk
    
    WHY THIS DESIGN:
        - Subclasses focus on architecture only
        - Common operations centralized
        - Easy to add new models (just implement build_model)
    """
    
    def __init__(
        self,
        input_shape: tuple = (224, 224, 3),
        num_classes: int = 1,
        freeze_base: bool = True
    ):
        """
        Initialize base model
        
        Args:
            input_shape: Input image shape (height, width, channels)
                DEFAULT: (224, 224, 3) - standard for ImageNet models
                WHY: Pre-trained models expect this size
                ALTERNATIVE: Variable sizes with adaptive pooling
                TRADE-OFF: Fixed size is simpler, variable is flexible
                
            num_classes: Number of output classes
                DEFAULT: 1 for binary classification (sigmoid)
                WHY: Fracture detection is binary (fracture/normal)
                ALTERNATIVE: 2 classes with softmax
                TRADE-OFF: 1 class simpler, 2 classes more explicit
                
            freeze_base: Whether to freeze pre-trained layers
                DEFAULT: True - freeze during initial training
                WHY: Prevents catastrophic forgetting
                STRATEGY: Freeze → train head → unfreeze → fine-tune
                IMPACT: Faster training, better transfer learning
        
        INITIALIZATION STRATEGY:
            Store configuration but don't build model yet
            WHY: Allows customization before building
            ALTERNATIVE: Build immediately (simpler but less flexible)
        """
        # Store configuration
        # WHY: Needed for model building and serialization
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.freeze_base = freeze_base
        
        # Model will be created by subclass
        # WHY: Each architecture builds differently
        # PATTERN: Template method pattern
        self.model: Optional[keras.Model] = None
        
        logger.info(f"Initialized {self.__class__.__name__}")
        logger.info(f"  Input shape: {input_shape}")
        logger.info(f"  Num classes: {num_classes}")
        logger.info(f"  Freeze base: {freeze_base}")
    
    @abstractmethod
    def build_model(self) -> keras.Model:
        """
        Build the model architecture
        
        PURPOSE:
            Abstract method that subclasses must implement
            
        WHY ABSTRACT:
            - Each model has different architecture
            - Forces subclasses to implement
            - Provides type safety
            
        IMPLEMENTATION REQUIREMENTS:
            1. Load pre-trained base model
            2. Freeze/unfreeze layers as needed
            3. Add custom classification head
            4. Return compiled model
            
        RETURNS:
            keras.Model: Constructed model
            
        RAISES:
            NotImplementedError: If subclass doesn't implement
        """
        pass
    
    def compile_model(
        self,
        optimizer: str = 'adam',
        learning_rate: float = 0.001,
        loss: str = 'binary_crossentropy',
        metrics: list = None
    ) -> None:
        """
        Compile the model with optimizer and loss
        
        PURPOSE:
            Configures model for training
            
        Args:
            optimizer: Optimizer name
                DEFAULT: 'adam' - adaptive learning rate
                WHY: Works well for most cases, requires less tuning
                ALTERNATIVES:
                    - 'sgd': Simpler, may need learning rate schedule
                    - 'rmsprop': Good for RNNs
                    - 'adamw': Adam with weight decay (better generalization)
                COMPARISON:
                    Adam: Fast convergence, good default
                    SGD: Better generalization, needs tuning
                    AdamW: Best of both, slightly slower
                    
            learning_rate: Initial learning rate
                DEFAULT: 0.001 (1e-3) - standard for Adam
                WHY: Balances speed and stability
                TUNING: Start here, reduce if unstable, increase if slow
                IMPACT: Too high → divergence, too low → slow training
                
            loss: Loss function
                DEFAULT: 'binary_crossentropy' for binary classification
                WHY: Proper loss for sigmoid output
                ALTERNATIVES:
                    - 'categorical_crossentropy': For softmax (multi-class)
                    - 'focal_loss': For class imbalance
                    - 'dice_loss': For segmentation
                TRADE-OFF: BCE is standard and well-understood
                
            metrics: List of metrics to track
                DEFAULT: ['accuracy', 'precision', 'recall', 'auc']
                WHY: Comprehensive evaluation
                MEDICAL AI: Recall (sensitivity) is critical!
                IMPACT: Tracks model performance during training
        
        COMPILATION PROCESS:
            1. Check model exists
            2. Create optimizer with learning rate
            3. Configure loss function
            4. Set metrics
            5. Call model.compile()
        
        WHY SEPARATE FROM BUILD:
            - Allows recompilation with different settings
            - Separates architecture from training config
            - Enables transfer learning workflows
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        # Default metrics for medical AI
        # WHY THESE METRICS:
        #   - Accuracy: Overall correctness
        #   - Precision: Avoid false alarms
        #   - Recall: Don't miss fractures (CRITICAL!)
        #   - AUC: Threshold-independent performance
        if metrics is None:
            metrics = [
                'accuracy',
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall'),  # Sensitivity
                keras.metrics.AUC(name='auc')
            ]
        
        # Create optimizer with learning rate
        # WHY: Allows customization of learning rate
        # ALTERNATIVE: Pass optimizer object directly
        if optimizer == 'adam':
            opt = keras.optimizers.Adam(learning_rate=learning_rate)
        elif optimizer == 'sgd':
            opt = keras.optimizers.SGD(
                learning_rate=learning_rate,
                momentum=0.9,  # Standard momentum value
                nesterov=True  # Better convergence
            )
        elif optimizer == 'adamw':
            opt = keras.optimizers.AdamW(
                learning_rate=learning_rate,
                weight_decay=0.01  # L2 regularization
            )
        else:
            # Fallback to string (Keras will handle)
            opt = optimizer
        
        # Compile model
        # WHY: Prepares model for training
        # IMPACT: Must be done before fit()
        self.model.compile(
            optimizer=opt,
            loss=loss,
            metrics=metrics
        )
        
        logger.info(f"Model compiled with {optimizer} optimizer (lr={learning_rate})")
    
    def summary(self) -> None:
        """
        Print model architecture summary
        
        PURPOSE:
            Displays layer-by-layer model structure
            
        WHY USEFUL:
            - Verify architecture is correct
            - Check parameter counts
            - Identify trainable vs frozen layers
            - Debug shape mismatches
            
        OUTPUT INCLUDES:
            - Layer names and types
            - Output shapes
            - Parameter counts
            - Total parameters (trainable/non-trainable)
            
        WHEN TO USE:
            - After building model
            - Before training (sanity check)
            - When debugging architecture issues
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        self.model.summary()
        
        # Additional statistics
        # WHY: Helps understand model complexity
        total_params = self.model.count_params()
        trainable_params = sum([keras.backend.count_params(w) 
                               for w in self.model.trainable_weights])
        
        logger.info(f"\nModel Statistics:")
        logger.info(f"  Total parameters: {total_params:,}")
        logger.info(f"  Trainable parameters: {trainable_params:,}")
        logger.info(f"  Non-trainable parameters: {total_params - trainable_params:,}")
        logger.info(f"  Trainable ratio: {trainable_params/total_params:.1%}")
    
    def save(self, filepath: str) -> None:
        """
        Save model to disk
        
        PURPOSE:
            Persists trained model for later use
            
        Args:
            filepath: Path to save model (.h5 or SavedModel format)
                FORMATS:
                    - .h5: HDF5 format (single file, legacy)
                    - SavedModel: TensorFlow format (directory, recommended)
                RECOMMENDATION: Use SavedModel for production
                
        WHY SAVE:
            - Preserve trained weights
            - Enable deployment
            - Resume training later
            - Share models with others
            
        WHAT'S SAVED:
            - Model architecture
            - Trained weights
            - Optimizer state (for resuming training)
            - Compilation config
            
        ALTERNATIVE:
            save_weights(): Only weights, not architecture
            TRADE-OFF: Smaller file but need code to rebuild
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    @staticmethod
    def load(filepath: str) -> keras.Model:
        """
        Load model from disk
        
        PURPOSE:
            Restores previously saved model
            
        Args:
            filepath: Path to saved model
            
        Returns:
            Loaded keras.Model
            
        WHY STATIC:
            - Don't need instance to load
            - Can load any model type
            - Simpler API
            
        USAGE:
            model = BaseModel.load('model.h5')
            
        ALTERNATIVE:
            Instance method: model.load(path)
            TRADE-OFF: Static is more flexible
        """
        model = keras.models.load_model(filepath)
        logger.info(f"Model loaded from {filepath}")
        return model
    
    def unfreeze_layers(self, num_layers: int = None) -> None:
        """
        Unfreeze top layers for fine-tuning
        
        PURPOSE:
            Enables fine-tuning of pre-trained model
            
        Args:
            num_layers: Number of top layers to unfreeze
                DEFAULT: None (unfreeze all)
                WHY: Gradual unfreezing prevents catastrophic forgetting
                STRATEGY: Start with few layers, gradually increase
                
        FINE-TUNING STRATEGY:
            Phase 1: Freeze all, train head (fast, stable)
            Phase 2: Unfreeze top N layers, fine-tune (better accuracy)
            Phase 3: Optionally unfreeze all (best accuracy, risky)
            
        WHY GRADUAL:
            - Prevents destroying pre-trained features
            - More stable training
            - Better final performance
            
        WHEN TO USE:
            - After initial training converges
            - When validation accuracy plateaus
            - For domain adaptation (ImageNet → X-rays)
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        if num_layers is None:
            # Unfreeze all layers
            # WHY: Maximum flexibility
            # RISK: May overfit or destroy features
            for layer in self.model.layers:
                layer.trainable = True
            logger.info("Unfroze all layers")
        else:
            # Unfreeze top N layers
            # WHY: Gradual adaptation
            # SAFER: Preserves low-level features
            total_layers = len(self.model.layers)
            for i, layer in enumerate(self.model.layers):
                if i >= total_layers - num_layers:
                    layer.trainable = True
                else:
                    layer.trainable = False
            logger.info(f"Unfroze top {num_layers} layers")
        
        # Must recompile after changing trainable status
        # WHY: Optimizer needs to know which weights to update
        # IMPACT: Forgetting this is a common bug!
        logger.warning("Remember to recompile model after unfreezing!")


if __name__ == "__main__":
    """
    Test code
    
    PURPOSE:
        Verify base class works correctly
        
    NOTE:
        Can't instantiate abstract class directly
        This is just for documentation
    """
    # This would raise TypeError
    # model = BaseModel()
    
    print("BaseModel is an abstract class")
    print("Use ResNet50Model, VGG16Model, or EfficientNetModel instead")
