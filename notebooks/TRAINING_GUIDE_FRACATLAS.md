# 🎯 FracAtlas Training Guide - Handling Imbalanced Dataset

## 📊 Dataset Challenge

Based on our EDA analysis:
- **Total Images**: 4,083
- **Fractured**: 717 (17.56%) ⚠️
- **Non-Fractured**: 3,366 (82.44%)
- **Imbalance Ratio**: 1:4.69 (HIGHLY IMBALANCED!)

This imbalance requires special handling to prevent the model from just predicting "non-fractured" all the time.

---

## 🎯 Recommended Models (Ranked)

### **1. EfficientNetB3** ⭐ (BEST CHOICE)
```python
Model: EfficientNetB3
Parameters: ~12M
Input Size: 300x300
Expected Accuracy: 94-95%
Training Time: ~2 hours (GPU) / ~8 hours (CPU)
```

**Why EfficientNetB3:**
- ✅ Best accuracy for medical imaging
- ✅ Handles imbalanced data well
- ✅ Moderate size (good for deployment)
- ✅ Fast inference
- ✅ Proven on X-ray images

### **2. ResNet50** ⭐ (RELIABLE BASELINE)
```python
Model: ResNet50
Parameters: ~25M
Input Size: 224x224
Expected Accuracy: 93-94%
Training Time: ~1.5 hours (GPU) / ~6 hours (CPU)
```

**Why ResNet50:**
- ✅ Most reliable and proven
- ✅ Excellent transfer learning
- ✅ Good documentation
- ✅ Easy to debug

### **3. EfficientNetB0** (LIGHTWEIGHT)
```python
Model: EfficientNetB0
Parameters: ~5M
Input Size: 224x224
Expected Accuracy: 92-93%
Training Time: ~1 hour (GPU) / ~4 hours (CPU)
```

**Why EfficientNetB0:**
- ✅ Fast training
- ✅ Small model size
- ✅ Good for laptops/limited hardware
- ✅ Quick experiments

---

## 🔧 Handling Imbalanced Data - CRITICAL!

### **Strategy 1: Class Weights** (RECOMMENDED) ⭐

```python
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

# Calculate class weights
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)

# Convert to dictionary
class_weight_dict = {
    0: class_weights[0],  # Non-fractured: ~0.6
    1: class_weights[1]   # Fractured: ~2.8
}

# Use in training
model.fit(
    train_data,
    class_weight=class_weight_dict,  # ← This is KEY!
    ...
)
```

### **Strategy 2: Focal Loss** (HIGHLY RECOMMENDED) ⭐⭐

```python
from src.training.losses import FocalLoss

# Focal Loss - designed for imbalanced data
loss = FocalLoss(
    alpha=0.75,  # Higher alpha = more weight on fractured class
    gamma=2.0    # Focus on hard examples
)

model.compile(
    optimizer='adam',
    loss=loss,  # ← Use Focal Loss instead of binary crossentropy
    metrics=['accuracy', 'AUC', 'Precision', 'Recall']
)
```

### **Strategy 3: Data Augmentation for Minority Class**

```python
# Augment fractured images MORE than non-fractured
fractured_augmentation = {
    'rotation_range': 20,      # More rotation
    'zoom_range': 0.15,        # More zoom
    'horizontal_flip': True,
    'vertical_flip': False,    # Don't flip X-rays vertically!
    'brightness_range': (0.7, 1.3),
    'width_shift_range': 0.1,
    'height_shift_range': 0.1,
    'shear_range': 0.1
}

# Less augmentation for non-fractured
non_fractured_augmentation = {
    'rotation_range': 10,
    'zoom_range': 0.1,
    'horizontal_flip': True,
    'brightness_range': (0.8, 1.2)
}
```

### **Strategy 4: Stratified Sampling**

```python
from sklearn.model_selection import train_test_split

# ALWAYS use stratified split!
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y,
    test_size=0.3,
    stratify=y,  # ← Maintains class distribution
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp,
    test_size=0.5,
    stratify=y_temp,  # ← Again, stratified!
    random_state=42
)
```

---

## 🚀 Complete Training Script (EfficientNetB3)

```python
#!/usr/bin/env python3
"""
FracAtlas Training Script - EfficientNetB3 with Imbalanced Data Handling
"""

import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

# Configuration
CONFIG = {
    'model_name': 'efficientnetb3',
    'input_size': 300,
    'batch_size': 16,  # Smaller for EfficientNetB3
    'epochs_phase1': 25,
    'epochs_phase2': 35,
    'learning_rate_phase1': 0.001,
    'learning_rate_phase2': 0.0001,
    'dropout_rate': 0.5,
    'focal_alpha': 0.75,  # High alpha for imbalanced data
    'focal_gamma': 2.0
}

def create_efficientnetb3_model(input_shape=(300, 300, 3), dropout_rate=0.5):
    """Create EfficientNetB3 model for fracture detection"""
    
    # Load pre-trained base
    base_model = EfficientNetB3(
        include_top=False,
        weights='imagenet',
        input_shape=input_shape
    )
    
    # Freeze base initially
    base_model.trainable = False
    
    # Add custom head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(dropout_rate)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(dropout_rate * 0.5)(x)
    output = Dense(1, activation='sigmoid')(x)  # Binary classification
    
    model = Model(inputs=base_model.input, outputs=output)
    
    return model, base_model

def focal_loss(alpha=0.75, gamma=2.0):
    """Focal Loss for imbalanced data"""
    def loss_fn(y_true, y_pred):
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
        
        # Calculate focal loss
        cross_entropy = -y_true * tf.math.log(y_pred)
        weight = alpha * tf.pow(1 - y_pred, gamma)
        loss = weight * cross_entropy
        
        return tf.reduce_mean(loss)
    
    return loss_fn

def main():
    print("=" * 80)
    print("🏥 FRACTURE DETECTION TRAINING - EfficientNetB3")
    print("=" * 80)
    
    # 1. Load Data (using your existing data loader)
    print("\n📂 Loading FracAtlas dataset...")
    from src.data.data_loader import FracAtlasDataLoader
    
    loader = FracAtlasDataLoader('data/raw/FracAtlas')
    train_data, val_data, test_data = loader.load_splits(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        stratified=True,  # IMPORTANT!
        random_seed=42
    )
    
    print(f"✅ Train: {len(train_data)} | Val: {len(val_data)} | Test: {len(test_data)}")
    
    # 2. Calculate Class Weights
    print("\n⚖️ Calculating class weights for imbalanced data...")
    y_train = train_data['labels']
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
    print(f"Class weights: Non-fractured={class_weights[0]:.2f}, Fractured={class_weights[1]:.2f}")
    
    # 3. Create Model
    print("\n🔨 Building EfficientNetB3 model...")
    model, base_model = create_efficientnetb3_model(
        input_shape=(CONFIG['input_size'], CONFIG['input_size'], 3),
        dropout_rate=CONFIG['dropout_rate']
    )
    
    # 4. Compile with Focal Loss
    print("\n⚙️ Compiling model with Focal Loss...")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(CONFIG['learning_rate_phase1']),
        loss=focal_loss(alpha=CONFIG['focal_alpha'], gamma=CONFIG['focal_gamma']),
        metrics=[
            'accuracy',
            tf.keras.metrics.AUC(name='auc'),
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall')
        ]
    )
    
    print(f"\n📊 Model Summary:")
    print(f"Total parameters: {model.count_params():,}")
    print(f"Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    
    # 5. Setup Callbacks
    callbacks = [
        ModelCheckpoint(
            'models/efficientnetb3_best.h5',
            monitor='val_recall',  # Monitor recall (sensitivity) for medical AI!
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
        )
    ]
    
    # 6. PHASE 1: Train with Frozen Base
    print("\n" + "=" * 80)
    print("🚀 PHASE 1: Training custom head (frozen base)")
    print("=" * 80)
    
    history_phase1 = model.fit(
        train_data,
        validation_data=val_data,
        epochs=CONFIG['epochs_phase1'],
        batch_size=CONFIG['batch_size'],
        class_weight=class_weight_dict,  # ← CRITICAL for imbalanced data!
        callbacks=callbacks,
        verbose=1
    )
    
    # Save phase 1 model
    model.save('models/efficientnetb3_phase1.h5')
    print("\n✅ Phase 1 complete! Model saved.")
    
    # 7. PHASE 2: Fine-tune Top Layers
    print("\n" + "=" * 80)
    print("🔥 PHASE 2: Fine-tuning top layers")
    print("=" * 80)
    
    # Unfreeze top 50 layers
    base_model.trainable = True
    for layer in base_model.layers[:-50]:
        layer.trainable = False
    
    print(f"Unfrozen top 50 layers")
    print(f"Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(CONFIG['learning_rate_phase2']),
        loss=focal_loss(alpha=CONFIG['focal_alpha'], gamma=CONFIG['focal_gamma']),
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
        epochs=CONFIG['epochs_phase2'],
        batch_size=CONFIG['batch_size'],
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    model.save('models/efficientnetb3_final.h5')
    print("\n✅ Phase 2 complete! Final model saved.")
    
    # 8. Evaluate on Test Set
    print("\n" + "=" * 80)
    print("📊 FINAL EVALUATION ON TEST SET")
    print("=" * 80)
    
    test_results = model.evaluate(test_data, batch_size=CONFIG['batch_size'])
    
    print("\n🎯 Test Results:")
    print(f"  Loss:      {test_results[0]:.4f}")
    print(f"  Accuracy:  {test_results[1]:.4f}")
    print(f"  AUC:       {test_results[2]:.4f}")
    print(f"  Precision: {test_results[3]:.4f}")
    print(f"  Recall:    {test_results[4]:.4f}")
    
    # Calculate F1 Score
    precision = test_results[3]
    recall = test_results[4]
    f1_score = 2 * (precision * recall) / (precision + recall)
    print(f"  F1 Score:  {f1_score:.4f}")
    
    print("\n" + "=" * 80)
    print("✅ TRAINING COMPLETE!")
    print("=" * 80)
    print("\n📁 Saved Models:")
    print("  - models/efficientnetb3_phase1.h5")
    print("  - models/efficientnetb3_best.h5")
    print("  - models/efficientnetb3_final.h5")
    
    print("\n🚀 Next Steps:")
    print("  1. Visualize training history")
    print("  2. Generate confusion matrix")
    print("  3. Create Grad-CAM visualizations")
    print("  4. Test on validation samples")
    print("  5. Deploy to API")

if __name__ == "__main__":
    main()
```

---

## 📝 Quick Start Commands

### **Option 1: Use Existing Training Script**
```bash
# Navigate to project
cd "d:\Coding Workspace\fracture detection ai"

# Train with ResNet50 (recommended for first try)
python scripts/train.py --model resnet50 --epochs 50 --batch-size 32

# Or train with EfficientNetB3 (best performance)
python scripts/train.py --model efficientnetb3 --epochs 60 --batch-size 16
```

### **Option 2: Custom Training**
```bash
# Create and run custom training script
python notebooks/train_fracatlas_custom.py
```

---

## ⚠️ Critical Settings for Imbalanced Data

### **MUST DO:**
1. ✅ **Use Class Weights** - Automatically balance the loss
2. ✅ **Use Focal Loss** - Focus on hard examples
3. ✅ **Stratified Sampling** - Maintain class distribution in splits
4. ✅ **Monitor Recall/Sensitivity** - More important than accuracy for medical AI
5. ✅ **Use AUC as primary metric** - Better for imbalanced data than accuracy

### **DON'T DO:**
1. ❌ Don't use plain binary crossentropy
2. ❌ Don't ignore class imbalance
3. ❌ Don't use accuracy as the only metric
4. ❌ Don't use random splits (always stratified!)
5. ❌ Don't skip validation on minority class

---

## 📊 Expected Results

### **Target Metrics (Imbalanced Dataset):**
```
Accuracy:    > 92%  (Don't trust this alone!)
AUC:         > 0.95 (Primary metric)
Sensitivity: > 94%  (CRITICAL - must detect fractures!)
Specificity: > 91%
F1 Score:    > 0.90
```

### **Training Timeline:**

**EfficientNetB3 (GPU):**
- Phase 1 (25 epochs): ~45 minutes
- Phase 2 (35 epochs): ~1.5 hours
- **Total: ~2.25 hours**

**ResNet50 (GPU):**
- Phase 1 (20 epochs): ~30 minutes
- Phase 2 (30 epochs): ~1 hour
- **Total: ~1.5 hours**

**CPU (i3 12th Gen):**
- Multiply GPU time by 4-5x
- EfficientNetB3: ~10 hours
- ResNet50: ~6-8 hours

---

## 🎯 Evaluation Checklist

After training, verify:

- [ ] **Sensitivity > 94%** (Can't miss fractures!)
- [ ] **AUC > 0.95** (Good discrimination)
- [ ] **No overfitting** (val_loss close to train_loss)
- [ ] **Confusion matrix looks good** (low false negatives)
- [ ] **ROC curve is smooth** (good across all thresholds)
- [ ] **Grad-CAM highlights fractures** (model is looking at right places)

---

## 🚀 Next Steps After Training

1. **Visualize Results**
   ```bash
   python scripts/visualize_results.py --model models/efficientnetb3_final.h5
   ```

2. **Generate Confusion Matrix**
   ```bash
   python scripts/evaluate_model.py --model models/efficientnetb3_final.h5
   ```

3. **Create Grad-CAM Visualizations**
   ```bash
   python scripts/generate_gradcam.py --model models/efficientnetb3_final.h5
   ```

4. **Deploy to API**
   ```bash
   cd deployment/api
   python app.py
   ```

---

**Ready to start training! Choose your model and run the training script.** 🚀
