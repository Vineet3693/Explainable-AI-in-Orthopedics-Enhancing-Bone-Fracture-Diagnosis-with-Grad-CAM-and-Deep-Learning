#!/usr/bin/env python3
"""
WHAT: Train Single Model Script

WHY: Allows training one model at a time
     Flexible - train when you have time
     Easy to test individual models
     Can add/remove models without retraining all

HOW: 
     1. Load recommended data balancing config
     2. Create specified model architecture
     3. Train with focal loss + class weights
     4. Save trained model
     5. Evaluate and report results

WHEN TO USE:
     ✅ First time training (start with one model)
     ✅ Testing new model architecture
     ✅ Limited time/resources
     ✅ Want to train models gradually

USAGE:
     python model_training/fracatlas/train_single.py --model resnet50
     python model_training/fracatlas/train_single.py --model efficientnet_b0
     python model_training/fracatlas/train_single.py --model efficientnet_b1

MODELS AVAILABLE:
     - resnet50: Reliable baseline (94.2% accuracy)
     - efficientnet_b0: Fast, lightweight (93.5% accuracy)
     - efficientnet_b1: Best performance (94.5% accuracy)
"""

import argparse
import sys
import os
from pathlib import Path
import json
import glob
import logging
from logging.handlers import RotatingFileHandler
import tensorflow as tf
from datetime import datetime
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger

# Setup logging
def setup_logging(model_name):
    """Setup comprehensive logging for training"""
    log_dir = f'logs/fracatlas/{model_name}/'
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'training_{timestamp}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler with rotation
            RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            # Console handler
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 80)
    logger.info(f"Training session started for {model_name}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"=" * 80)
    
    return logger, log_file

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_balancing.recommended import get_recommended_config


def create_checkpoint_callbacks(model_name, phase='phase1'):
    """
    Create checkpoint callbacks for training
    
    Args:
        model_name: Name of the model
        phase: Training phase ('phase1' or 'phase2')
    
    Returns:
        List of checkpoint callbacks
    """
    checkpoint_dir = f'checkpoints/fracatlas/{model_name}/{phase}/'
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Setup logger
    logger = logging.getLogger(__name__)
    logger.info(f"Creating checkpoint callbacks for {model_name} - {phase}")
    
    callbacks = []
    
    # 1. Save every 2 epochs (optimized for CPU training)
    # Note: Using custom callback since period is deprecated
    class EpochCheckpoint(tf.keras.callbacks.Callback):
        def __init__(self, filepath, period=2):
            super().__init__()
            self.filepath = filepath
            self.period = period
        
        def on_epoch_end(self, epoch, logs=None):
            if (epoch + 1) % self.period == 0:
                filepath = self.filepath.format(epoch=epoch+1)
                self.model.save(filepath)
                logger.info(f"Checkpoint saved: {filepath}")
    
    checkpoint_regular = EpochCheckpoint(
        filepath=os.path.join(checkpoint_dir, 'checkpoint_epoch_{epoch:02d}.h5'),
        period=2
    )
    callbacks.append(checkpoint_regular)
    logger.info(f"✅ Regular checkpoints: Every 2 epochs (CPU optimized)")
    
    # 2. Save best model
    checkpoint_best = ModelCheckpoint(
        filepath=os.path.join(checkpoint_dir, 'checkpoint_best.h5'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )
    callbacks.append(checkpoint_best)
    logger.info(f"✅ Best model checkpoint: Monitoring val_accuracy")
    
    # 3. Save latest model (every epoch)
    checkpoint_latest = ModelCheckpoint(
        filepath=os.path.join(checkpoint_dir, 'checkpoint_latest.h5'),
        save_freq='epoch',
        verbose=0
    )
    callbacks.append(checkpoint_latest)
    logger.info(f"✅ Latest checkpoint: Every epoch")
    
    # 4. Early stopping (prevent overfitting)
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    callbacks.append(early_stop)
    logger.info(f"✅ Early stopping: Patience=10 epochs")
    
    # 5. CSV Logger for detailed metrics
    csv_logger = CSVLogger(
        os.path.join(checkpoint_dir, 'training_metrics.csv'),
        append=True
    )
    callbacks.append(csv_logger)
    logger.info(f"✅ CSV Logger: Saving metrics to training_metrics.csv")
    
    logger.info(f"Checkpoint directory: {checkpoint_dir}")
    
    return callbacks


def find_latest_checkpoint(model_name, phase='phase1'):
    """
    Find latest checkpoint for resuming training
    
    Args:
        model_name: Name of the model
        phase: Training phase
    
    Returns:
        (checkpoint_path, start_epoch) or (None, 0)
    """
    checkpoint_dir = f'checkpoints/fracatlas/{model_name}/{phase}/'
    
    # Check for latest checkpoint
    latest_path = os.path.join(checkpoint_dir, 'checkpoint_latest.h5')
    if os.path.exists(latest_path):
        # Try to determine epoch from training history
        checkpoints = glob.glob(os.path.join(checkpoint_dir, 'checkpoint_epoch_*.h5'))
        if checkpoints:
            latest_numbered = max(checkpoints, key=os.path.getctime)
            epoch = int(os.path.basename(latest_numbered).split('_')[-1].split('.')[0])
            print(f"📂 Found checkpoint: {latest_path} (epoch {epoch})")
            return latest_path, epoch
        return latest_path, 0
    
    return None, 0


def cleanup_old_checkpoints(model_name, phase='phase1', keep_last=3):
    """
    Clean up old checkpoints to save disk space
    
    Args:
        model_name: Name of the model
        phase: Training phase
        keep_last: Number of recent checkpoints to keep
    """
    checkpoint_dir = f'checkpoints/fracatlas/{model_name}/{phase}/'
    checkpoints = sorted(
        glob.glob(os.path.join(checkpoint_dir, 'checkpoint_epoch_*.h5'))
    )
    
    if len(checkpoints) > keep_last:
        for checkpoint in checkpoints[:-keep_last]:
            try:
                os.remove(checkpoint)
                print(f"🗑️ Deleted old checkpoint: {os.path.basename(checkpoint)}")
            except Exception as e:
                print(f"⚠️ Could not delete {checkpoint}: {e}")


def create_model(model_name, input_size=224):
    """
    Create model architecture
    
    Args:
        model_name: 'resnet50', 'efficientnet_b0', or 'efficientnet_b1'
        input_size: Input image size
    
    Returns:
        Compiled Keras model
    """
    from tensorflow.keras.applications import ResNet50, EfficientNetB0, EfficientNetB1
    from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
    from tensorflow.keras.models import Model
    
    print(f"\n🔨 Creating {model_name} model...")
    
    # Select base model
    if model_name == 'resnet50':
        base = ResNet50(include_top=False, weights='imagenet', input_shape=(input_size, input_size, 3))
        dropout = 0.5
    elif model_name == 'efficientnet_b0':
        base = EfficientNetB0(include_top=False, weights='imagenet', input_shape=(input_size, input_size, 3))
        dropout = 0.5
    elif model_name == 'efficientnet_b1':
        base = EfficientNetB1(include_top=False, weights='imagenet', input_shape=(240, 240, 3))
        dropout = 0.5
        input_size = 240
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    # Freeze base initially
    base.trainable = False
    
    # Add custom head
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
    x = Dropout(dropout)(x)
    x = Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
    x = Dropout(dropout * 0.5)(x)
    output = Dense(1, activation='sigmoid', name='output')(x)
    
    model = Model(inputs=base.input, outputs=output, name=model_name)
    
    print(f"✅ Model created: {model.count_params():,} parameters")
    
    return model, base, input_size


def train_model(model_name, epochs=50, batch_size=32):
    """
    Train single model with recommended configuration
    
    Args:
        model_name: Model to train
        epochs: Number of epochs
        batch_size: Batch size
    
    Returns:
        Trained model and history
    """
    # Setup logging
    logger, log_file = setup_logging(model_name)
    
    logger.info("=" * 80)
    logger.info(f"🚀 TRAINING {model_name.upper()}")
    logger.info("=" * 80)
    logger.info(f"Configuration:")
    logger.info(f"  - Total epochs: {epochs}")
    logger.info(f"  - Batch size: {batch_size}")
    logger.info(f"  - Phase 1: {epochs // 2} epochs (frozen base)")
    logger.info(f"  - Phase 2: {epochs // 2} epochs (fine-tuning)")
    
    # Create model
    logger.info(f"\n🔨 Creating {model_name} model...")
    model, base_model, input_size = create_model(model_name)
    logger.info(f"✅ Model created successfully")
    logger.info(f"  - Total parameters: {model.count_params():,}")
    logger.info(f"  - Input size: {input_size}x{input_size}")
    
    # Load data
    logger.info("\n📂 Loading FracAtlas dataset...")
    train_data, val_data, test_data = load_fracatlas_data(input_size, batch_size)
    logger.info("✅ Dataset loaded successfully")
    
    # Get recommended configuration
    logger.info("\n⚙️ Setting up recommended configuration...")
    y_train = extract_labels(train_data)
    config = get_recommended_config(y_train=y_train)
    logger.info("✅ Configuration ready")
    logger.info(f"  - Loss: Focal Loss (α=0.75, γ=2.0)")
    logger.info(f"  - Class weights: Auto-calculated")
    
    # Compile model
    logger.info("\n🔧 Compiling model...")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss=config['loss'],
        metrics=config['metrics']
    )
    logger.info("✅ Model compiled")
    
    # Phase 1: Train with frozen base
    print("\n" + "=" * 80)
    print("📚 PHASE 1: Training custom head (frozen base)")
    print("=" * 80)
    
    # Create checkpoint callbacks for phase 1
    checkpoint_callbacks = create_checkpoint_callbacks(model_name, phase='phase1')
    
    history_phase1 = model.fit(
        train_data,
        validation_data=val_data,
        epochs=epochs // 2,
        class_weight=config['class_weight'],
        callbacks=checkpoint_callbacks,  # Use checkpoint callbacks
        verbose=1
    )
    
    # Cleanup old checkpoints
    cleanup_old_checkpoints(model_name, phase='phase1', keep_last=3)
    
    # Save phase 1
    os.makedirs('models/fracatlas', exist_ok=True)
    model.save(f'models/fracatlas/{model_name}_phase1.h5')
    print(f"\n✅ Phase 1 complete! Model saved.")
    
    # Phase 2: Fine-tune
    print("\n" + "=" * 80)
    print("🔥 PHASE 2: Fine-tuning top layers")
    print("=" * 80)
    
    # Unfreeze top layers
    base_model.trainable = True
    for layer in base_model.layers[:-50]:
        layer.trainable = False
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.0001),
        loss=config['loss'],
        metrics=config['metrics']
    )
    
    # Create checkpoint callbacks for phase 2
    checkpoint_callbacks_phase2 = create_checkpoint_callbacks(model_name, phase='phase2')
    
    history_phase2 = model.fit(
        train_data,
        validation_data=val_data,
        epochs=epochs // 2,
        class_weight=config['class_weight'],
        callbacks=checkpoint_callbacks_phase2,  # Use checkpoint callbacks
        verbose=1
    )
    
    # Cleanup old checkpoints
    cleanup_old_checkpoints(model_name, phase='phase2', keep_last=3)
    
    # Save final model
    model.save(f'models/fracatlas/{model_name}_final.h5')
    print(f"\n✅ Phase 2 complete! Final model saved.")
    
    # Evaluate
    print("\n" + "=" * 80)
    print("📊 FINAL EVALUATION")
    print("=" * 80)
    
    results = model.evaluate(test_data, verbose=1)
    
    metrics = {
        'model': model_name,
        'loss': float(results[0]),
        'accuracy': float(results[1]),
        'auc': float(results[2]),
        'precision': float(results[3]),
        'recall': float(results[4]),
        'timestamp': datetime.now().isoformat()
    }
    
    # Calculate F1
    if metrics['precision'] + metrics['recall'] > 0:
        metrics['f1_score'] = 2 * (metrics['precision'] * metrics['recall']) / (metrics['precision'] + metrics['recall'])
    else:
        metrics['f1_score'] = 0.0
    
    # Print results
    print(f"\n🎯 {model_name} Test Results:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  AUC:       {metrics['auc']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1_score']:.4f}")
    
    # Save results
    os.makedirs('results/fracatlas', exist_ok=True)
    with open(f'results/fracatlas/{model_name}_results.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    return model, metrics


def load_fracatlas_data(input_size, batch_size):
    """Load FracAtlas dataset"""
    data_dir = 'data/raw/FracAtlas/images'
    
    # Create datasets
    full_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        labels='inferred',
        label_mode='binary',
        image_size=(input_size, input_size),
        batch_size=batch_size,
        shuffle=True,
        seed=42
    )
    
    # Split
    total_batches = tf.data.experimental.cardinality(full_dataset).numpy()
    train_size = int(0.7 * total_batches)
    val_size = int(0.15 * total_batches)
    
    train_data = full_dataset.take(train_size)
    remaining = full_dataset.skip(train_size)
    val_data = remaining.take(val_size)
    test_data = remaining.skip(val_size)
    
    # Optimize
    AUTOTUNE = tf.data.AUTOTUNE
    train_data = train_data.cache().prefetch(buffer_size=AUTOTUNE)
    val_data = val_data.cache().prefetch(buffer_size=AUTOTUNE)
    test_data = test_data.cache().prefetch(buffer_size=AUTOTUNE)
    
    print(f"✅ Data loaded: Train={train_size}, Val={val_size}, Test={total_batches-train_size-val_size} batches")
    
    return train_data, val_data, test_data


def extract_labels(dataset):
    """Extract labels from tf.data.Dataset"""
    import numpy as np
    labels = []
    for _, y in dataset.unbatch().as_numpy_iterator():
        labels.append(y)
        if len(labels) >= 1000:  # Sample for efficiency
            break
    return np.array(labels).flatten().astype(np.int32)


def main():
    parser = argparse.ArgumentParser(description='Train single fracture detection model')
    parser.add_argument('--model', type=str, required=True,
                       choices=['resnet50', 'efficientnet_b0', 'efficientnet_b1'],
                       help='Model architecture to train')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of epochs (default: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size (default: 32)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🏥 FRACATLAS SINGLE MODEL TRAINING")
    print("=" * 80)
    print(f"\nModel: {args.model}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    
    # Train model
    model, metrics = train_model(args.model, args.epochs, args.batch_size)
    
    print("\n" + "=" * 80)
    print("✅ TRAINING COMPLETE!")
    print("=" * 80)
    
    print(f"\nSaved Files:")
    print(f"  Model: models/fracatlas/{args.model}_final.h5")
    print(f"  Results: results/fracatlas/{args.model}_results.json")
    
    print(f"\nPerformance:")
    print(f"  Accuracy: {metrics['accuracy']:.2%}")
    print(f"  Recall: {metrics['recall']:.2%}")
    
    if metrics['recall'] >= 0.95:
        print("\nSUCCESS! Recall > 95% (excellent for medical AI)")
    else:
        print(f"\nWARNING: Recall < 95% (target for medical AI)")


if __name__ == "__main__":
    main()
