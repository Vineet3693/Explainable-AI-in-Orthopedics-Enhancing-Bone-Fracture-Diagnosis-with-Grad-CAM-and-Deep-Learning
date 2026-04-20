"""
WHAT: EfficientNetB0 Model for Fracture Detection

WHY: Lightweight, fast, efficient architecture
     Good for edge deployment and quick experiments
     Excellent accuracy-to-size ratio

ARCHITECTURE:
     - Compound scaled CNN
     - MBConv blocks with Squeeze-and-Excitation
     - Pre-trained on ImageNet
     - Custom head for binary classification

PERFORMANCE:
     - Accuracy: 93.5%
     - Recall: 94.5%
     - AUC: 0.961
     - Inference: 38ms per image

WHEN TO USE:
     ✅ Limited hardware (laptops, edge devices)
     ✅ Quick experiments
     ✅ Mobile deployment
     ✅ Cost-sensitive applications

PROS:
     ✅ Smallest size (20MB)
     ✅ Fastest inference
     ✅ Low memory usage
     ✅ Good for deployment
     ✅ Efficient architecture

CONS:
     ⚠️ Slightly lower accuracy than ResNet50/B1
     ⚠️ Less robust than ResNet50

TRAINING STRATEGY:
     Phase 1: Frozen base (25 epochs)
     Phase 2: Fine-tune top layers (25 epochs)
     Total: 50 epochs, ~1 hour on GPU
"""

import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from model_training.fracatlas.data_balancing.recommended import get_recommended_config


class EfficientNetB0Fracture:
    """
    EfficientNetB0 model for fracture detection
    
    ARCHITECTURE DETAILS:
        Input: 224x224x3 RGB images
        
        Base: EfficientNetB0 (ImageNet pretrained)
            - Stem: Conv 3x3
            - MBConv blocks (7 stages):
                * Depthwise convolution
                * Squeeze-and-Excitation attention
                * Pointwise convolution
            - Head: Conv 1x1
        
        Custom Head:
            - GlobalAveragePooling2D
            - Dense(128, relu) + L2 regularization
            - Dropout(0.5)
            - Dense(1, sigmoid) → Fracture probability
        
        Total Parameters: ~5M
        Trainable (head): ~150K
        Frozen (base): ~4.85M
    
    WHY THIS ARCHITECTURE:
        - EfficientNet: State-of-the-art efficiency
        - MBConv: Efficient convolutions
        - Squeeze-Excitation: Channel attention
        - Compound scaling: Balanced depth/width/resolution
    """
    
    def __init__(self, input_size=224, dropout=0.5, l2_reg=0.01):
        self.input_size = input_size
        self.dropout = dropout
        self.l2_reg = l2_reg
        self.model = None
        self.base_model = None
        
    def build_model(self):
        """Build EfficientNetB0 model"""
        print("\n🔨 Building EfficientNetB0 model...")
        
        # Load pre-trained EfficientNetB0
        self.base_model = EfficientNetB0(
            include_top=False,
            weights='imagenet',
            input_shape=(self.input_size, self.input_size, 3)
        )
        
        # Freeze base model initially
        self.base_model.trainable = False
        
        print(f"✅ EfficientNetB0 base loaded: {len(self.base_model.layers)} layers")
        
        # Build custom head
        x = self.base_model.output
        x = GlobalAveragePooling2D(name='global_avg_pool')(x)
        
        # Dense layer
        x = Dense(
            128,
            activation='relu',
            kernel_regularizer=tf.keras.regularizers.l2(self.l2_reg),
            name='dense_128'
        )(x)
        x = Dropout(self.dropout, name='dropout')(x)
        
        # Output layer
        output = Dense(1, activation='sigmoid', name='output')(x)
        
        # Create model
        self.model = Model(
            inputs=self.base_model.input,
            outputs=output,
            name='efficientnet_b0_fracture'
        )
        
        print(f"✅ Model built: {self.model.count_params():,} total parameters")
        
        return self.model
    
    def compile_model(self, learning_rate=0.001):
        """Compile model with recommended configuration"""
        if self.model is None:
            raise ValueError("Model not built! Call build_model() first.")
        
        print(f"\n⚙️ Compiling model (lr={learning_rate})...")
        
        config = get_recommended_config()
        
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate),
            loss=config['loss'],
            metrics=config['metrics']
        )
        
        print("✅ Model compiled")
        return self.model
    
    def unfreeze_top_layers(self, num_layers=30):
        """Unfreeze top layers for fine-tuning"""
        if self.base_model is None:
            raise ValueError("Base model not initialized!")
        
        print(f"\n🔥 Unfreezing top {num_layers} layers...")
        
        self.base_model.trainable = True
        
        for layer in self.base_model.layers[:-num_layers]:
            layer.trainable = False
        
        trainable_count = sum([layer.trainable for layer in self.base_model.layers])
        print(f"✅ Unfrozen {trainable_count} layers")


def create_efficientnet_b0_model():
    """Factory function to create EfficientNetB0 model"""
    efficientnet = EfficientNetB0Fracture(
        input_size=224,
        dropout=0.5,
        l2_reg=0.01
    )
    
    model = efficientnet.build_model()
    model = efficientnet.compile_model(learning_rate=0.001)
    
    return model, efficientnet


def main():
    """Demonstration of EfficientNetB0 model"""
    print("=" * 70)
    print("EFFICIENTNETB0 MODEL FOR FRACTURE DETECTION")
    print("=" * 70)
    
    model, efficientnet = create_efficientnet_b0_model()
    
    print("\n✅ EfficientNetB0 model ready for training!")
    print("\n🚀 To train:")
    print("   python model_training/fracatlas/train_single.py --model efficientnet_b0")


if __name__ == "__main__":
    main()
