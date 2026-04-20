# 💾 Checkpoint Strategy - Complete Guide

## 🎯 Recommended Checkpoint Strategy

### **For 50 Epochs Training:**

**Save checkpoints every 5 epochs** ✅

**Why 5 epochs?**
- ✅ Good balance (safety vs disk space)
- ✅ Max loss: 30 minutes (GPU) or 2 hours (CPU)
- ✅ Only 10 checkpoint files (manageable)
- ✅ ~1-2GB total disk space

---

## 📊 Checkpoint Frequency Comparison

| Frequency | Checkpoints | Disk Space | Max Loss (GPU) | Max Loss (CPU) | Recommended? |
|-----------|------------|------------|----------------|----------------|--------------|
| **Every epoch** | 50 files | 5GB | 5 min | 20 min | ❌ Too many files |
| **Every 2 epochs** | 25 files | 2.5GB | 10 min | 40 min | ⚠️ Good but large |
| **Every 5 epochs** | 10 files | 1GB | 30 min | 2 hours | ✅ **OPTIMAL** |
| **Every 10 epochs** | 5 files | 500MB | 1 hour | 4 hours | ⚠️ Risky |
| **Best only** | 1 file | 100MB | All progress | All progress | ❌ Too risky |

---

## 💡 Recommended Strategy

### **3-Tier Checkpoint System:**

```
1. Regular Checkpoints (Every 5 epochs)
   - checkpoint_epoch_05.h5
   - checkpoint_epoch_10.h5
   - checkpoint_epoch_15.h5
   - etc.

2. Best Model (Continuous)
   - checkpoint_best.h5
   - Saved whenever validation improves

3. Latest Model (Continuous)
   - checkpoint_latest.h5
   - Always has most recent state
```

---

## 📁 Checkpoint Structure

### **Directory Layout:**

```
checkpoints/fracatlas/
├── resnet50/
│   ├── checkpoint_epoch_05.h5
│   ├── checkpoint_epoch_10.h5
│   ├── checkpoint_epoch_15.h5
│   ├── checkpoint_epoch_20.h5
│   ├── checkpoint_epoch_25.h5
│   ├── checkpoint_epoch_30.h5
│   ├── checkpoint_epoch_35.h5
│   ├── checkpoint_epoch_40.h5
│   ├── checkpoint_epoch_45.h5
│   ├── checkpoint_epoch_50.h5
│   ├── checkpoint_best.h5      ← Best performing
│   ├── checkpoint_latest.h5    ← Most recent
│   └── training_log.json       ← Progress tracking
│
├── efficientnet_b0/
│   └── [same structure]
│
└── efficientnet_b1/
    └── [same structure]
```

---

## 🔧 Implementation

### **Checkpoint Callbacks:**

```python
from tensorflow.keras.callbacks import ModelCheckpoint
import os

# Create checkpoint directory
checkpoint_dir = f'checkpoints/fracatlas/{model_name}/'
os.makedirs(checkpoint_dir, exist_ok=True)

# 1. Save every 5 epochs
checkpoint_regular = ModelCheckpoint(
    filepath=os.path.join(checkpoint_dir, 'checkpoint_epoch_{epoch:02d}.h5'),
    save_freq='epoch',
    period=5,  # Every 5 epochs
    verbose=1,
    save_weights_only=False  # Save full model
)

# 2. Save best model
checkpoint_best = ModelCheckpoint(
    filepath=os.path.join(checkpoint_dir, 'checkpoint_best.h5'),
    monitor='val_accuracy',
    save_best_only=True,
    mode='max',
    verbose=1
)

# 3. Save latest model
checkpoint_latest = ModelCheckpoint(
    filepath=os.path.join(checkpoint_dir, 'checkpoint_latest.h5'),
    save_freq='epoch',
    verbose=0
)

# Use all callbacks
callbacks = [checkpoint_regular, checkpoint_best, checkpoint_latest]
```

---

## 🔄 Resume Training

### **Auto-Resume Function:**

```python
def get_latest_checkpoint(model_name):
    """Find latest checkpoint for model"""
    checkpoint_dir = f'checkpoints/fracatlas/{model_name}/'
    
    # Check for latest checkpoint
    latest_path = os.path.join(checkpoint_dir, 'checkpoint_latest.h5')
    if os.path.exists(latest_path):
        return latest_path, get_epoch_from_checkpoint(latest_path)
    
    # Check for numbered checkpoints
    checkpoints = glob.glob(os.path.join(checkpoint_dir, 'checkpoint_epoch_*.h5'))
    if checkpoints:
        latest = max(checkpoints, key=os.path.getctime)
        epoch = int(latest.split('_')[-1].split('.')[0])
        return latest, epoch
    
    return None, 0

def resume_training(model_name, total_epochs=50):
    """Resume training from checkpoint"""
    checkpoint_path, start_epoch = get_latest_checkpoint(model_name)
    
    if checkpoint_path:
        print(f"📂 Found checkpoint: {checkpoint_path}")
        print(f"✅ Resuming from epoch {start_epoch + 1}")
        model = tf.keras.models.load_model(checkpoint_path)
    else:
        print("🆕 No checkpoint found. Starting fresh...")
        model = create_model(model_name)
        start_epoch = 0
    
    # Train from start_epoch to total_epochs
    history = model.fit(
        train_data,
        validation_data=val_data,
        epochs=total_epochs,
        initial_epoch=start_epoch,  # Resume from here!
        callbacks=callbacks
    )
    
    return model, history
```

---

## 📊 Checkpoint Scenarios

### **Scenario 1: Training Interrupted at Epoch 17**

```
Training Progress:
Epoch 1-5:   Complete → checkpoint_epoch_05.h5 saved
Epoch 6-10:  Complete → checkpoint_epoch_10.h5 saved
Epoch 11-15: Complete → checkpoint_epoch_15.h5 saved
Epoch 16-17: Training → INTERRUPTED! ⚡

Resume:
→ Load checkpoint_latest.h5 (epoch 17)
→ Continue from epoch 18
→ Lost: 0 epochs ✅
```

### **Scenario 2: Training Interrupted at Epoch 23**

```
Training Progress:
Epoch 1-20:  Complete → checkpoint_epoch_20.h5 saved
Epoch 21-23: Training → INTERRUPTED! ⚡

Resume:
→ Load checkpoint_latest.h5 (epoch 23)
→ Continue from epoch 24
→ Lost: 0 epochs ✅
```

### **Scenario 3: Checkpoint Corrupted**

```
Training Progress:
Epoch 1-25:  Complete → checkpoint_epoch_25.h5 saved
Epoch 26-28: Training → CRASH! ❌
             → checkpoint_latest.h5 corrupted

Resume:
→ checkpoint_latest.h5 corrupted
→ Load checkpoint_epoch_25.h5 (fallback)
→ Continue from epoch 26
→ Lost: 3 epochs (18 min GPU, 1.5h CPU)
```

---

## 💾 Disk Space Management

### **Space Requirements:**

```
Per Model (50 epochs, save every 5):
- 10 regular checkpoints: 10 × 100MB = 1GB
- 1 best checkpoint: 100MB
- 1 latest checkpoint: 100MB
Total per model: ~1.2GB

All 3 Models:
- ResNet50: 1.2GB
- EfficientNetB0: 300MB
- EfficientNetB1: 400MB
Total: ~2GB

Recommendation: Have 5GB free space
```

### **Auto-Cleanup Strategy:**

```python
def cleanup_old_checkpoints(model_name, keep_last=3):
    """Keep only last N regular checkpoints"""
    checkpoint_dir = f'checkpoints/fracatlas/{model_name}/'
    checkpoints = sorted(
        glob.glob(os.path.join(checkpoint_dir, 'checkpoint_epoch_*.h5'))
    )
    
    # Keep last N, delete rest
    if len(checkpoints) > keep_last:
        for checkpoint in checkpoints[:-keep_last]:
            os.remove(checkpoint)
            print(f"🗑️ Deleted old checkpoint: {os.path.basename(checkpoint)}")
    
    # Always keep best and latest
    # Don't delete checkpoint_best.h5 or checkpoint_latest.h5
```

---

## 🎯 Checkpoint Best Practices

### **DO:**

✅ **Save every 5 epochs** (good balance)
```python
period=5
```

✅ **Save best model** (always have backup)
```python
save_best_only=True
monitor='val_accuracy'
```

✅ **Save latest model** (for resume)
```python
save_freq='epoch'
```

✅ **Keep last 3 checkpoints** (safety net)
```python
cleanup_old_checkpoints(keep_last=3)
```

✅ **Test resume before long training**
```python
# Train for 10 epochs
# Stop manually
# Resume and verify it works
```

### **DON'T:**

❌ **Don't save every epoch** (too many files)
```python
period=1  # Avoid this!
```

❌ **Don't save only best** (may lose progress)
```python
# Don't use ONLY this:
save_best_only=True
```

❌ **Don't delete all checkpoints** (keep backups)
```python
# Keep at least 2-3 checkpoints
```

❌ **Don't ignore disk space** (monitor usage)
```python
# Check available space before training
```

---

## 📋 Training Commands

### **With Checkpoints:**

```bash
# First run (starts fresh)
python train_single.py --model resnet50 --epochs 50

# If interrupted, resume automatically
python train_single.py --model resnet50 --epochs 50 --resume

# Resume from specific checkpoint
python train_single.py --model resnet50 --epochs 50 \
    --checkpoint checkpoints/fracatlas/resnet50/checkpoint_epoch_25.h5
```

---

## 🔍 Monitoring Checkpoints

### **Check Checkpoint Status:**

```python
def list_checkpoints(model_name):
    """List all checkpoints for model"""
    checkpoint_dir = f'checkpoints/fracatlas/{model_name}/'
    
    print(f"\n📂 Checkpoints for {model_name}:")
    print("-" * 60)
    
    # Regular checkpoints
    checkpoints = sorted(
        glob.glob(os.path.join(checkpoint_dir, 'checkpoint_epoch_*.h5'))
    )
    for cp in checkpoints:
        size = os.path.getsize(cp) / (1024**2)  # MB
        mtime = datetime.fromtimestamp(os.path.getmtime(cp))
        print(f"  {os.path.basename(cp):<30} {size:>6.1f}MB  {mtime}")
    
    # Best checkpoint
    best_path = os.path.join(checkpoint_dir, 'checkpoint_best.h5')
    if os.path.exists(best_path):
        size = os.path.getsize(best_path) / (1024**2)
        print(f"  checkpoint_best.h5{' '*16} {size:>6.1f}MB  (Best model)")
    
    # Latest checkpoint
    latest_path = os.path.join(checkpoint_dir, 'checkpoint_latest.h5')
    if os.path.exists(latest_path):
        size = os.path.getsize(latest_path) / (1024**2)
        print(f"  checkpoint_latest.h5{' '*14} {size:>6.1f}MB  (Latest)")
    
    print("-" * 60)
```

---

## ✅ Final Recommendation

### **Optimal Checkpoint Strategy:**

```python
# For 50 epochs training:

1. Save every 5 epochs
   - Creates 10 checkpoints
   - Max loss: 30 min (GPU) or 2 hours (CPU)
   - Disk space: ~1GB per model

2. Save best model
   - Always have best performing model
   - Can use even if training incomplete

3. Save latest model
   - For seamless resume
   - Updated every epoch

4. Keep last 3 regular checkpoints
   - Safety net for corruption
   - Saves disk space

5. Auto-resume on restart
   - Detects checkpoints automatically
   - Continues from last epoch
```

---

## 🚀 Implementation Summary

### **What We'll Add:**

1. **ModelCheckpoint callbacks** (every 5 epochs)
2. **Best model saving** (continuous)
3. **Latest model saving** (continuous)
4. **Auto-resume function** (detect and load)
5. **Checkpoint cleanup** (manage disk space)
6. **Progress tracking** (JSON log)

### **Benefits:**

✅ Safe interruption (can stop anytime)
✅ Quick resume (from last checkpoint)
✅ Minimal loss (max 5 epochs)
✅ Disk efficient (~1-2GB)
✅ Automatic (no manual intervention)

---

**Ready to implement this checkpoint system in the training scripts!** 🎉

Would you like me to update `train_single.py` and `train_all.py` with this checkpoint functionality?
