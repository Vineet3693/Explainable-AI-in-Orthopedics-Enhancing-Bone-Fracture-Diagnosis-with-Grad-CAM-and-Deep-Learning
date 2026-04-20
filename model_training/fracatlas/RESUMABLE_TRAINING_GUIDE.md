# 🔄 Resumable Training Guide - Train in Multiple Sessions

## Yes, You Can Split Training Across Days!

Thanks to our checkpoint system, you can:
- ✅ Train for 2 hours today
- ✅ Stop training anytime
- ✅ Resume tomorrow from exactly where you stopped
- ✅ No progress lost!

---

## How It Works

### Automatic Checkpoints:
Our system saves checkpoints **every 2 epochs** automatically:

```
Training Timeline:
├─ Epoch 2 ✅ Checkpoint saved
├─ Epoch 4 ✅ Checkpoint saved  
├─ Epoch 6 ✅ Checkpoint saved
├─ ... (you can stop here)
└─ Resume next day from Epoch 6!
```

### What Gets Saved:
1. **Model weights** - Complete model state
2. **Training progress** - Which epoch you're on
3. **Best model** - Best performing version
4. **Metrics** - All training history

---

## Example: Split 50-Epoch Training

### Day 1 (2 hours):
```bash
# Start training
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16

# After 2 hours, press Ctrl+C to stop
# Checkpoints saved: Epochs 2, 4, 6, 8, 10, 12, 14, 16, 18, 20
```

**Progress:** ~20 epochs completed (40% done)

### Day 2 (2 hours):
```bash
# Resume from checkpoint
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16 --resume

# Continues from Epoch 20
# Completes: Epochs 21-40
```

**Progress:** 40 epochs total (80% done)

### Day 3 (1 hour):
```bash
# Resume again
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16 --resume

# Completes: Epochs 41-50
```

**Done!** ✅

---

## Checkpoint Safety Features

### Every 2 Epochs:
- ✅ Regular checkpoint saved
- ✅ Can resume from this point
- ✅ Max loss: 2 epochs (~30 min)

### Every Epoch:
- ✅ Latest checkpoint saved
- ✅ Always have most recent state

### Best Model:
- ✅ Best performing model saved
- ✅ Restored if training stops

---

## How to Resume Training

### Method 1: Automatic Resume (Recommended)
```bash
# Just run the same command again
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16

# Script automatically detects checkpoint and resumes
```

### Method 2: Manual Resume
```bash
# Specify checkpoint file
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --resume-from checkpoints/fracatlas/efficientnet_b0/phase1/checkpoint_latest.h5
```

---

## Training Schedule Examples

### Schedule 1: Daily 2-Hour Sessions
```
Day 1: Epochs 1-20   (2 hours)
Day 2: Epochs 21-40  (2 hours)
Day 3: Epochs 41-50  (1 hour)
Total: 5 hours over 3 days
```

### Schedule 2: Short Daily Sessions
```
Day 1: Epochs 1-10   (1 hour)
Day 2: Epochs 11-20  (1 hour)
Day 3: Epochs 21-30  (1 hour)
Day 4: Epochs 31-40  (1 hour)
Day 5: Epochs 41-50  (1 hour)
Total: 5 hours over 5 days
```

### Schedule 3: Weekend Training
```
Saturday: Epochs 1-30  (3 hours)
Sunday:   Epochs 31-50 (2 hours)
Total: 5 hours over 2 days
```

---

## What Happens If You Stop Training?

### Scenario 1: Stop at Epoch 10
```
✅ Checkpoints saved:
   - checkpoint_epoch_02.h5
   - checkpoint_epoch_04.h5
   - checkpoint_epoch_06.h5
   - checkpoint_epoch_08.h5
   - checkpoint_epoch_10.h5
   - checkpoint_latest.h5
   - checkpoint_best.h5

✅ Resume from: Epoch 10
✅ Progress lost: 0 epochs!
```

### Scenario 2: Stop at Epoch 11 (between checkpoints)
```
✅ Checkpoints saved:
   - checkpoint_epoch_10.h5
   - checkpoint_latest.h5 (Epoch 11)

✅ Resume from: Epoch 11
✅ Progress lost: 0 epochs!
```

### Scenario 3: Computer Crashes at Epoch 15
```
✅ Checkpoints saved:
   - checkpoint_epoch_14.h5
   - checkpoint_latest.h5 (Epoch 14)

✅ Resume from: Epoch 14
✅ Progress lost: 1 epoch (~15 min)
```

---

## Results Are Always Saved

### During Training:
- ✅ Checkpoints every 2 epochs
- ✅ Latest checkpoint every epoch
- ✅ Best model when validation improves
- ✅ Metrics logged to CSV

### After Each Session:
- ✅ All checkpoints preserved
- ✅ Training history saved
- ✅ Can review progress anytime

### Final Results:
- ✅ Final model saved
- ✅ Complete metrics saved
- ✅ Training logs saved
- ✅ Nothing lost!

---

## Checkpoint Locations

```
checkpoints/fracatlas/efficientnet_b0/
├── phase1/
│   ├── checkpoint_epoch_02.h5  ← Resume from here
│   ├── checkpoint_epoch_04.h5
│   ├── checkpoint_epoch_06.h5
│   ├── checkpoint_epoch_08.h5
│   ├── checkpoint_epoch_10.h5
│   ├── checkpoint_best.h5      ← Best model
│   ├── checkpoint_latest.h5    ← Most recent
│   └── training_metrics.csv    ← All metrics
└── phase2/
    └── [same structure]
```

---

## Practical Example

### Today (2 hours available):
```bash
# Start training at 1:00 PM
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16

# At 3:00 PM (2 hours later), press Ctrl+C
# Completed: ~20 epochs
# Saved: All checkpoints up to Epoch 20
```

### Tomorrow (2 hours available):
```bash
# Start at 10:00 AM
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16

# Script detects checkpoint at Epoch 20
# Resumes from Epoch 21
# At 12:00 PM, completed up to Epoch 40
```

### Day After (1 hour available):
```bash
# Start at 2:00 PM
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16

# Resumes from Epoch 40
# At 3:00 PM, training complete!
# Final model saved ✅
```

---

## Safety Guarantees

### No Data Loss:
- ✅ Checkpoints saved automatically
- ✅ Can't lose more than 2 epochs
- ✅ Best model always preserved

### Flexible Scheduling:
- ✅ Train anytime, any duration
- ✅ Stop/resume unlimited times
- ✅ No need for continuous training

### Progress Tracking:
- ✅ CSV metrics show all epochs
- ✅ Logs show exact progress
- ✅ Can review anytime

---

## Commands Summary

### Start Training:
```bash
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16
```

### Stop Training:
```
Press Ctrl+C
(Checkpoint automatically saved)
```

### Resume Training:
```bash
# Same command - auto-resumes
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16
```

### Check Progress:
```bash
# View metrics
type checkpoints\fracatlas\efficientnet_b0\phase1\training_metrics.csv

# View logs
type logs\fracatlas\efficientnet_b0\training_*.log
```

---

## Recommended Approach

### For Your Schedule:

**Option 1: Daily 2-Hour Sessions**
```
Day 1: Train 2 hours (Epochs 1-20)
Day 2: Train 2 hours (Epochs 21-40)
Day 3: Train 1 hour  (Epochs 41-50)
```

**Option 2: Flexible Sessions**
```
Session 1: 30 min (Epochs 1-5)
Session 2: 1 hour  (Epochs 6-15)
Session 3: 2 hours (Epochs 16-35)
Session 4: 1.5 hours (Epochs 36-50)
```

**Both work perfectly!** ✅

---

## Bottom Line

✅ **You can split training across multiple days**  
✅ **Checkpoints save every 2 epochs automatically**  
✅ **Resume anytime with same command**  
✅ **No progress lost**  
✅ **Results always saved**  

**Train at your convenience - the system handles everything!**

---

**Ready to start?**
```bash
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50 --batch-size 16
```

**Stop anytime with Ctrl+C, resume later with the same command!**
