"""
ResNet50 model for fracture detection
"""

import tensorflow as tf
from tensorflow import keras
from src.models.base_model import BaseModel


class ResNet50Model(BaseModel):
    """
    ResNet50-based fracture detection model
    
    ARCHITECTURE:
        Input (224x224x3)
        ↓
        ResNet50 Base (frozen/unfrozen)
        ↓
        GlobalAveragePooling2D
        ↓
        Dense(512) + ReLU + BatchNorm + Dropout
        ↓
        Dense(256) + ReLU + BatchNorm + Dropout
        ↓
        Dense(1) + Sigmoid (binary classification)
    
    DESIGN DECISIONS:
        1. GlobalAveragePooling vs Flatten:
           - GAP reduces parameters (no spatial info needed)
           - Prevents overfitting
           - Standard practice for transfer learning
        
        2. Two Dense layers (512 → 256):
           - Gradual dimensionality reduction
           - More capacity to learn task-specific features
           - Alternative: Single dense layer (faster but less flexible)
        
        3. BatchNormalization:
           - Stabilizes training
           - Allows higher learning rates
           - Slight regularization effect
        
        4. Dropout (0.5, 0.3):
           - Prevents overfitting
           - Different rates for different layers
           - Higher dropout early (more parameters)
    
    TRANSFER LEARNING STRATEGY:
        Phase 1: Freeze base, train head (fast, prevents catastrophic forgetting)
        Phase 2: Unfreeze top layers, fine-tune (better accuracy)
        
        WHY: Preserves low-level features (edges, textures) learned from ImageNet
             while adapting high-level features to X-rays
    """
    
    def __init__(
        self,
        input_shape=(224, 224, 3),
        num_classes=1,
        freeze_base=True,
        dropout_rate=0.5
    ):
        super().__init__(input_shape, num_classes, freeze_base)
        self.dropout_rate = dropout_rate
    
    def build_model(self) -> keras.Model:
        """Build ResNet50 model with custom head"""
        
        # Load pre-trained ResNet50
        base_model = keras.applications.ResNet50(
            include_top=False,
            weights='imagenet',
            input_shape=self.input_shape
        )
        
        # Freeze base model if specified
        base_model.trainable = not self.freeze_base
        
        # Build custom head
        inputs = keras.Input(shape=self.input_shape)
        
        # Base model
        x = base_model(inputs, training=False)
        
        # Custom classification head
        x = keras.layers.GlobalAveragePooling2D()(x)
        x = keras.layers.Dense(512, activation='relu')(x)
        x = keras.layers.BatchNormalization()(x)
        x = keras.layers.Dropout(self.dropout_rate)(x)
        x = keras.layers.Dense(256, activation='relu')(x)
        x = keras.layers.BatchNormalization()(x)
        x = keras.layers.Dropout(self.dropout_rate * 0.6)(x)
        
        # Output layer
        if self.num_classes == 1:
            outputs = keras.layers.Dense(1, activation='sigmoid')(x)
        else:
            outputs = keras.layers.Dense(self.num_classes, activation='softmax')(x)
        
        # Create model
        self.model = keras.Model(inputs=inputs, outputs=outputs, name='ResNet50_Fracture')
        
        print(f"ResNet50 model built successfully")
        print(f"Total layers: {len(self.model.layers)}")
        print(f"Trainable: {sum([1 for layer in self.model.layers if layer.trainable])}")
        
        return self.model


if __name__ == "__main__":
    # Test model creation
    model = ResNet50Model(
        input_shape=(224, 224, 3),
        num_classes=1,
        freeze_base=True,
        dropout_rate=0.5
    )
    
    model.build_model()
    model.compile_model(
        optimizer='adam',
        learning_rate=0.0001,
        loss='binary_crossentropy'
    )
    
    model.summary()
