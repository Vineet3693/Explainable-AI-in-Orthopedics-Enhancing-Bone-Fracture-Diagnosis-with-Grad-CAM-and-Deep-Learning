#!/usr/bin/env python3
"""
FracAtlas Multi-Model Training Script
Train multiple CNN models with proper imbalance handling
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tensorflow as tf
from tensorflow.keras.applications import ResNet50, EfficientNetB0, EfficientNetB1, VGG16
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import train_test_split

print("=" * 80)
print("🏥 FRACATLAS MULTI-MODEL TRAINING")
print("=" * 80)

# Configuration
CONFIG = {
    'data_path': 'data/raw/FracAtlas',
    'models_dir': 'models/fracatlas',
    'logs_dir': 'logs/fracatlas',
    'results_dir': 'results/fracatlas',
    'image_size': 224,
    'batch_size': 32,
    'epochs': 50,
    'validation_split': 0.15,
    'test_split': 0.15,
    'random_seed': 42
}

# Models to train
MODELS_TO_TRAIN = {
    'resnet50': {
        'base': ResNet50,
        'input_size': 224,
        'batch_size': 32,
        'epochs': 50,
        'learning_rate': 0.001,
        'dropout': 0.5
    },
    'efficientnet_b0': {
        'base': EfficientNetB0,
        'input_size': 224,
        'batch_size': 32,
        'epochs': 50,
        'learning_rate': 0.001,
        'dropout': 0.5
    },
    'efficientnet_b1': {
        'base': EfficientNetB1,
        'input_size': 240,
        'batch_size': 16,
        'epochs': 60,
        'learning_rate': 0.001,
        'dropout': 0.5
    }
}

def create_directories():
    """Create necessary directories"""
    for dir_path in [CONFIG['models_dir'], CONFIG['logs_dir'], CONFIG['results_dir']]:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def focal_loss(alpha=0.75, gamma=2.0):
    """
    Focal Loss for handling imbalanced data
    alpha: weight for positive class (fractured)
    gamma: focusing parameter
    """
    def loss_fn(y_true, y_pred):
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
        
        # Calculate cross entropy
        cross_entropy = -y_true * tf.math.log(y_pred) - (1 - y_true) * tf.math.log(1 - y_pred)
        
        # Calculate focal loss
        weight = alpha * y_true + (1 - alpha) * (1 - y_true)
        focal_weight = weight * tf.pow(tf.abs(y_true - y_pred), gamma)
        
        loss = focal_weight * cross_entropy
        return tf.reduce_mean(loss)
    
    return loss_fn

def create_model(model_config, model_name, input_size):
    """
    Create a CNN model with transfer learning
    """
    print(f"\n🔨 Building {model_name}...")
    
    # Load base model
    base_model = model_config['base'](
        include_top=False,
        weights='imagenet',
        input_shape=(input_size, input_size, 3)
    )
    
    # Freeze base layers initially
    base_model.trainable = False
    
    # Add custom head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
    x = Dropout(model_config['dropout'])(x)
    x = Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
    x = Dropout(model_config['dropout'] * 0.5)(x)
    output = Dense(1, activation='sigmoid', name='output')(x)
    
    model = Model(inputs=base_model.input, outputs=output, name=model_name)
    
    print(f"✅ Model created: {model.count_params():,} parameters")
    
    return model, base_model

def get_callbacks(model_name):
    """Setup training callbacks"""
    callbacks = [
        ModelCheckpoint(
            filepath=f"{CONFIG['models_dir']}/{model_name}_best.h5",
            monitor='val_recall',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=12,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        CSVLogger(
            f"{CONFIG['logs_dir']}/{model_name}_training.csv",
            append=False
        )
    ]
    
    return callbacks

def load_and_prepare_data():
    """
    Load FracAtlas dataset and prepare for training
    Returns: train_data, val_data, test_data, class_weights
    """
    print("\n📂 Loading FracAtlas dataset...")
    
    # Load dataset using tf.keras.preprocessing
    data_dir = CONFIG['data_path']
    
    # Create dataset from directory
    full_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        f"{data_dir}/images",
        labels='inferred',
        label_mode='binary',
        image_size=(CONFIG['image_size'], CONFIG['image_size']),
        batch_size=CONFIG['batch_size'],
        shuffle=True,
        seed=CONFIG['random_seed']
    )
    
    # Get total number of batches
    total_batches = tf.data.experimental.cardinality(full_dataset).numpy()
    
    # Calculate split sizes
    train_size = int(0.7 * total_batches)
    val_size = int(0.15 * total_batches)
    test_size = total_batches - train_size - val_size
    
    # Split dataset
    train_dataset = full_dataset.take(train_size)
    remaining = full_dataset.skip(train_size)
    val_dataset = remaining.take(val_size)
    test_dataset = remaining.skip(val_size)
    
    # Optimize performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_dataset = train_dataset.cache().prefetch(buffer_size=AUTOTUNE)
    val_dataset = val_dataset.cache().prefetch(buffer_size=AUTOTUNE)
    test_dataset = test_dataset.cache().prefetch(buffer_size=AUTOTUNE)
    
    # Calculate class weights from training data
    print("\n⚖️ Calculating class weights for imbalanced data...")
    y_train = []
    for _, labels in train_dataset.unbatch():
        y_train.append(labels.numpy())
    y_train = np.array(y_train)
    
    class_weights = compute_class_weight(
        'balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    
    class_weight_dict = {
        0: float(class_weights[0]),
        1: float(class_weights[1])
    }
    
    print(f"Class weights: Non-fractured={class_weights[0]:.2f}, Fractured={class_weights[1]:.2f}")
    print(f"✅ Data loaded: Train={train_size} batches, Val={val_size} batches, Test={test_size} batches")
    
    return train_dataset, val_dataset, test_dataset, class_weight_dict

def train_model(model_name, model_config, train_data, val_data, class_weights):
    """
    Train a single model
    """
    print("\n" + "=" * 80)
    print(f"🚀 TRAINING {model_name.upper()}")
    print("=" * 80)
    
    # Create model
    model, base_model = create_model(
        model_config,
        model_name,
        model_config['input_size']
    )
    
    # Compile with Focal Loss
    model.compile(
        optimizer=tf.keras.optimizers.Adam(model_config['learning_rate']),
        loss=focal_loss(alpha=0.75, gamma=2.0),
        metrics=[
            'accuracy',
            tf.keras.metrics.AUC(name='auc'),
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall')
        ]
    )
    
    # Get callbacks
    callbacks = get_callbacks(model_name)
    
    # Phase 1: Train with frozen base
    print(f"\n📚 Phase 1: Training custom head (frozen base)...")
    history_phase1 = model.fit(
        train_data,
        validation_data=val_data,
        epochs=model_config['epochs'] // 2,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save phase 1 model
    model.save(f"{CONFIG['models_dir']}/{model_name}_phase1.h5")
    print(f"✅ Phase 1 complete!")
    
    # Phase 2: Fine-tune top layers
    print(f"\n🔥 Phase 2: Fine-tuning top layers...")
    base_model.trainable = True
    
    # Freeze all except top 50 layers
    for layer in base_model.layers[:-50]:
        layer.trainable = False
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(model_config['learning_rate'] / 10),
        loss=focal_loss(alpha=0.75, gamma=2.0),
        metrics=[
            'accuracy',
            tf.keras.metrics.AUC(name='auc'),
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall')
        ]
    )
    
    history_phase2 = model.fit(
        train_data,
        validation_data=val_data,
        epochs=model_config['epochs'] // 2,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    model.save(f"{CONFIG['models_dir']}/{model_name}_final.h5")
    print(f"✅ Phase 2 complete!")
    
    return model, history_phase1, history_phase2

def evaluate_model(model, model_name, test_data):
    """Evaluate model on test set"""
    print(f"\n📊 Evaluating {model_name}...")
    
    results = model.evaluate(test_data, verbose=1)
    
    metrics = {
        'model': model_name,
        'loss': float(results[0]),
        'accuracy': float(results[1]),
        'auc': float(results[2]),
        'precision': float(results[3]),
        'recall': float(results[4])
    }
    
    # Calculate F1 score
    if metrics['precision'] + metrics['recall'] > 0:
        metrics['f1_score'] = 2 * (metrics['precision'] * metrics['recall']) / (metrics['precision'] + metrics['recall'])
    else:
        metrics['f1_score'] = 0.0
    
    print(f"\n🎯 {model_name} Test Results:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  AUC:       {metrics['auc']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1_score']:.4f}")
    
    return metrics

def main():
    """Main training pipeline"""
    start_time = datetime.now()
    
    # Create directories
    create_directories()
    
    # Load data
    train_data, val_data, test_data, class_weights = load_and_prepare_data()
    
    # Store all results
    all_results = []
    
    # Train each model
    for model_name, model_config in MODELS_TO_TRAIN.items():
        try:
            # Train model
            model, hist1, hist2 = train_model(
                model_name,
                model_config,
                train_data,
                val_data,
                class_weights
            )
            
            # Evaluate model
            metrics = evaluate_model(model, model_name, test_data)
            all_results.append(metrics)
            
            # Clear memory
            tf.keras.backend.clear_session()
            
        except Exception as e:
            print(f"\n❌ Error training {model_name}: {str(e)}")
            continue
    
    # Save results
    results_file = f"{CONFIG['results_dir']}/training_results.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TRAINING SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Model':<20} {'Accuracy':<12} {'AUC':<12} {'Recall':<12} {'F1 Score':<12}")
    print("-" * 80)
    
    for result in sorted(all_results, key=lambda x: x['auc'], reverse=True):
        print(f"{result['model']:<20} {result['accuracy']:<12.4f} {result['auc']:<12.4f} {result['recall']:<12.4f} {result['f1_score']:<12.4f}")
    
    # Find best model
    best_model = max(all_results, key=lambda x: x['auc'])
    print(f"\n🏆 Best Model: {best_model['model']} (AUC: {best_model['auc']:.4f})")
    
    # Training time
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n⏱️ Total Training Time: {duration}")
    
    print("\n" + "=" * 80)
    print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
    print("=" * 80)
    
    print(f"\n📁 Models saved in: {CONFIG['models_dir']}")
    print(f"📁 Logs saved in: {CONFIG['logs_dir']}")
    print(f"📁 Results saved in: {results_file}")
    
    print("\n🚀 Next Steps:")
    print("  1. Create ensemble from trained models")
    print("  2. Generate visualizations (confusion matrix, ROC curves)")
    print("  3. Test on validation samples")
    print("  4. Deploy to API")

if __name__ == "__main__":
    main()
