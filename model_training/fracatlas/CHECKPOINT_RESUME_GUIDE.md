# 🔄 Training Interruption & Resume Guide

## ⚠️ **CURRENT BEHAVIOR (Without Checkpoints)**

### **What Happens If You Stop Training:**

**Bad News:** 
- ❌ Training starts from **BEGINNING** if interrupted
- ❌ All progress is **LOST**
- ❌ Have to train for full 17 hours again
- ❌ Wasted time and electricity

**Example:**
```
Hour 0:  Start training
Hour 10: Power cut / Laptop shutdown / Ctrl+C
         → All 10 hours of training LOST!
Hour 11: Restart training
         → Starts from epoch 1 again (not epoch 20)
```

---

## ✅ **SOLUTION: Checkpoint & Resume**

### **What We Need to Add:**

**Checkpoints** = Saving model progress periodically

**Benefits:**
- ✅ Resume from last checkpoint
- ✅ Don't lose progress
- ✅ Safe interruption
- ✅ Recover from crashes

---

## 🎯 **How Checkpoints Work**

### **During Training:**

```
Epoch 1:  Train → Save checkpoint
Epoch 2:  Train → Save checkpoint
Epoch 3:  Train → Save checkpoint
...
Epoch 10: Train → Save checkpoint → INTERRUPTED!

Resume Training:
Epoch 11: Load checkpoint → Continue from epoch 11
Epoch 12: Train → Save checkpoint
...
```

### **Checkpoint Files:**

```
checkpoints/fracatlas/resnet50/
├── checkpoint_epoch_01.h5
├── checkpoint_epoch_05.h5
├── checkpoint_epoch_10.h5  ← Load this to resume
├── checkpoint_epoch_15.h5
└── checkpoint_best.h5      ← Best model so far
```

---

## 📋 **Implementation Guide**

### **Method 1: ModelCheckpoint Callback (Recommended)**

```python
from tensorflow.keras.callbacks import ModelCheckpoint

# Save checkpoint every 5 epochs
checkpoint_callback = ModelCheckpoint(
    filepath='checkpoints/fracatlas/{model_name}/checkpoint_epoch_{epoch:02d}.h5',
    save_freq='epoch',
    save_best_only=False,  # Save all checkpoints
    verbose=1
)

# Save best model
best_checkpoint = ModelCheckpoint(
    filepath='checkpoints/fracatlas/{model_name}/checkpoint_best.h5',
    save_best_only=True,  # Only save if better
    monitor='val_loss',
    mode='min',
    verbose=1
)

# Use in training
model.fit(
    train_data,
    validation_data=val_data,
    epochs=50,
    callbacks=[checkpoint_callback, best_checkpoint]
)
```

### **Method 2: Manual Checkpointing**

```python
import os

# Check if checkpoint exists
checkpoint_path = f'checkpoints/fracatlas/{model_name}/latest.h5'

if os.path.exists(checkpoint_path):
    print("📂 Found checkpoint! Resuming training...")
    model = tf.keras.models.load_model(checkpoint_path)
    initial_epoch = load_epoch_number(checkpoint_path)
else:
    print("🆕 No checkpoint found. Starting fresh...")
    model = create_model(model_name)
    initial_epoch = 0

# Train from initial_epoch
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=50,
    initial_epoch=initial_epoch,  # Resume from here!
    callbacks=[checkpoint_callback]
)
```

---

## 🔧 **Updated Training Script**

I'll create an updated version with checkpoint support:

### **Key Features:**

1. **Auto-save every 5 epochs**
2. **Save best model**
3. **Auto-resume if checkpoint exists**
4. **Progress tracking**
5. **Safe interruption**

### **Usage:**

```bash
# First run (starts from beginning)
python train_single.py --model resnet50

# If interrupted at epoch 15
# Second run (resumes from epoch 15)
python train_single.py --model resnet50 --resume
```

---

## 📊 **Checkpoint Strategies**

### **Strategy 1: Save Every Epoch (Safe but Large)**

```python
# Saves after every epoch
# Pros: Can resume from any epoch
# Cons: Takes a lot of disk space (50 checkpoints × 100MB = 5GB)

save_freq='epoch'
```

### **Strategy 2: Save Every N Epochs (Balanced)**

```python
# Saves every 5 epochs
# Pros: Less disk space
# Cons: May lose up to 5 epochs of progress

class CustomCheckpoint(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        if (epoch + 1) % 5 == 0:  # Every 5 epochs
            self.model.save(f'checkpoint_epoch_{epoch+1:02d}.h5')
```

### **Strategy 3: Save Best Only (Minimal)**

```python
# Saves only when model improves
# Pros: Minimal disk space
# Cons: May not have recent checkpoint

save_best_only=True
monitor='val_loss'
```

### **Recommended: Combination**

```python
# Save every 5 epochs + best model
callbacks = [
    ModelCheckpoint(  # Every 5 epochs
        filepath='checkpoint_epoch_{epoch:02d}.h5',
        save_freq=5,
        verbose=1
    ),
    ModelCheckpoint(  # Best model
        filepath='checkpoint_best.h5',
        save_best_only=True,
        monitor='val_loss',
        verbose=1
    )
]
```

---

## 💾 **Disk Space Requirements**

### **Per Checkpoint:**

| Model | Size per Checkpoint |
|-------|-------------------|
| ResNet50 | ~100MB |
| EfficientNetB0 | ~25MB |
| EfficientNetB1 | ~35MB |

### **Total Space (50 epochs, save every 5):**

| Model | Checkpoints | Total Space |
|-------|------------|-------------|
| ResNet50 | 10 files | ~1GB |
| EfficientNetB0 | 10 files | ~250MB |
| EfficientNetB1 | 10 files | ~350MB |

### **All 3 Models:**
- Total: ~1.6GB for checkpoints
- Recommendation: Have 5GB free space

---

## 🚨 **Common Interruption Scenarios**

### **Scenario 1: Power Cut**

```
Training at epoch 15/50
→ Power cut
→ Laptop shuts down
→ Last checkpoint: epoch 10

Resume:
→ Load checkpoint_epoch_10.h5
→ Continue from epoch 11
→ Lost: 5 epochs (30 minutes)
→ Saved: 10 epochs (1 hour)
```

### **Scenario 2: Ctrl+C (Manual Stop)**

```
Training at epoch 20/50
→ Press Ctrl+C
→ Training stops gracefully
→ Last checkpoint: epoch 20

Resume:
→ Load checkpoint_epoch_20.h5
→ Continue from epoch 21
→ Lost: 0 epochs
→ Perfect resume!
```

### **Scenario 3: Laptop Overheating**

```
Training at epoch 25/50
→ Laptop too hot (>95°C)
→ Automatic shutdown
→ Last checkpoint: epoch 25

Resume:
→ Let laptop cool (30 min)
→ Load checkpoint_epoch_25.h5
→ Continue from epoch 26
→ Lost: 0 epochs
```

### **Scenario 4: Crash/Error**

```
Training at epoch 30/50
→ Python crashes
→ Last checkpoint: epoch 30

Resume:
→ Fix error
→ Load checkpoint_epoch_30.h5
→ Continue from epoch 31
→ Lost: 0 epochs
```

---

## 📝 **Resume Training Steps**

### **Step 1: Check for Checkpoints**

```bash
# List available checkpoints
ls checkpoints/fracatlas/resnet50/

# Output:
checkpoint_epoch_05.h5
checkpoint_epoch_10.h5
checkpoint_epoch_15.h5  ← Latest
checkpoint_best.h5
```

### **Step 2: Resume Training**

```bash
# Auto-resume from latest checkpoint
python train_single.py --model resnet50 --resume

# Or specify checkpoint
python train_single.py --model resnet50 --checkpoint checkpoint_epoch_15.h5
```

### **Step 3: Verify Resume**

```
📂 Found checkpoint: checkpoint_epoch_15.h5
✅ Loaded model from epoch 15
🔄 Resuming training from epoch 16...

Epoch 16/50
[=====>........................] - ETA: 2:30
```

---

## 🎯 **Best Practices**

### **DO:**

✅ **Save checkpoints every 5 epochs**
- Balance between safety and disk space
- Can resume with minimal loss

✅ **Save best model separately**
- Always have best performing model
- Can use even if training incomplete

✅ **Keep last 3 checkpoints**
- Delete older checkpoints to save space
- Keep recent ones for safety

✅ **Test resume functionality**
- Stop training manually
- Verify resume works
- Before long training sessions

✅ **Monitor disk space**
- Ensure enough space for checkpoints
- Clean old checkpoints periodically

### **DON'T:**

❌ **Don't delete all checkpoints**
- Keep at least the best one
- You may need to resume

❌ **Don't save too frequently**
- Every epoch = too much disk space
- Every 5 epochs is good balance

❌ **Don't ignore checkpoint errors**
- If checkpoint fails to save, investigate
- May indicate disk space issues

---

## 🔧 **Checkpoint Management**

### **Auto-cleanup Old Checkpoints:**

```python
import glob
import os

def cleanup_old_checkpoints(model_name, keep_last=3):
    """Keep only last N checkpoints"""
    checkpoint_dir = f'checkpoints/fracatlas/{model_name}/'
    checkpoints = sorted(glob.glob(f'{checkpoint_dir}checkpoint_epoch_*.h5'))
    
    # Keep last N, delete rest
    if len(checkpoints) > keep_last:
        for checkpoint in checkpoints[:-keep_last]:
            os.remove(checkpoint)
            print(f"🗑️ Deleted old checkpoint: {checkpoint}")
```

### **Checkpoint Info:**

```python
def get_checkpoint_info(checkpoint_path):
    """Get info about checkpoint"""
    import h5py
    
    with h5py.File(checkpoint_path, 'r') as f:
        # Get training info
        epoch = f.attrs.get('epoch', 0)
        loss = f.attrs.get('loss', 0)
        accuracy = f.attrs.get('accuracy', 0)
    
    print(f"Checkpoint: {checkpoint_path}")
    print(f"  Epoch: {epoch}")
    print(f"  Loss: {loss:.4f}")
    print(f"  Accuracy: {accuracy:.4f}")
```

---

## 📊 **Progress Tracking**

### **Training Log:**

```
checkpoints/fracatlas/resnet50/training_log.json
```

```json
{
  "model": "resnet50",
  "start_time": "2024-12-21 10:00:00",
  "total_epochs": 50,
  "completed_epochs": 15,
  "last_checkpoint": "checkpoint_epoch_15.h5",
  "best_val_loss": 0.234,
  "best_epoch": 12,
  "interrupted": true,
  "resume_count": 1
}
```

---

## ✅ **Summary**

### **Current Behavior (No Checkpoints):**
- ❌ Stops = Start from beginning
- ❌ All progress lost
- ❌ Risky for long training

### **With Checkpoints:**
- ✅ Stops = Resume from checkpoint
- ✅ Minimal progress lost
- ✅ Safe for long training

### **Recommendation:**

**For 17-hour CPU training:**
1. ✅ **Enable checkpoints** (save every 5 epochs)
2. ✅ **Save best model** (always have backup)
3. ✅ **Test resume** (before long training)
4. ✅ **Monitor disk space** (need ~2GB)

---

## 🚀 **Next Steps**

I'll create an updated training script with:
1. ✅ Automatic checkpointing
2. ✅ Resume functionality
3. ✅ Progress tracking
4. ✅ Checkpoint management

**This will make your 17-hour training much safer!** 🎉

---

**Want me to implement this now?** Let me know! 🚀
