# ⏱️ Model Training Time Estimates - FracAtlas

## 📊 Dataset Information
- **Total Images:** 4,083
- **Training Set:** ~2,858 images (70%)
- **Validation Set:** ~612 images (15%)
- **Test Set:** ~613 images (15%)
- **Batch Size:** 32 (ResNet50, EfficientNetB0), 16 (EfficientNetB1)

---

## 🖥️ Hardware Scenarios

### **Scenario 1: GPU Training (NVIDIA RTX 3060 or similar)**

#### Individual Model Training Times:

| Model | Phase 1 (Frozen) | Phase 2 (Fine-tune) | Total | Per Epoch |
|-------|-----------------|---------------------|-------|-----------|
| **ResNet50** | 45 min (25 epochs) | 50 min (25 epochs) | **~1.5 hours** | ~1.8 min |
| **EfficientNetB0** | 30 min (25 epochs) | 35 min (25 epochs) | **~1.0 hour** | ~1.3 min |
| **EfficientNetB1** | 45 min (30 epochs) | 50 min (30 epochs) | **~1.5 hours** | ~1.5 min |

#### Training All Models Sequentially:
```
ResNet50:        1.5 hours
EfficientNetB0:  1.0 hour
EfficientNetB1:  1.5 hours
─────────────────────────────
TOTAL:           4.0 hours
```

**Best Case:** 3.5-4 hours  
**Worst Case:** 4.5-5 hours (if any issues)

---

### **Scenario 2: CPU Training (i3 12th Gen or similar)**

#### Individual Model Training Times:

| Model | Phase 1 (Frozen) | Phase 2 (Fine-tune) | Total | Per Epoch |
|-------|-----------------|---------------------|-------|-----------|
| **ResNet50** | 3 hours (25 epochs) | 3.5 hours (25 epochs) | **~6.5 hours** | ~7.8 min |
| **EfficientNetB0** | 2 hours (25 epochs) | 2.5 hours (25 epochs) | **~4.5 hours** | ~5.4 min |
| **EfficientNetB1** | 3 hours (30 epochs) | 3.5 hours (30 epochs) | **~6.5 hours** | ~6.5 min |

#### Training All Models Sequentially:
```
ResNet50:        6.5 hours
EfficientNetB0:  4.5 hours
EfficientNetB1:  6.5 hours
─────────────────────────────
TOTAL:           17.5 hours
```

**Best Case:** 16-17 hours  
**Worst Case:** 18-20 hours

---

## 🚀 Parallel Training (Multiple GPUs)

### If you have 3 GPUs:

**Train all models simultaneously:**
```
All 3 models in parallel: ~1.5 hours
(Limited by slowest model: ResNet50 or EfficientNetB1)
```

**Time Saved:** 2.5 hours (vs sequential)

### If you have 2 GPUs:

**Option 1:** Train 2 models, then 1
```
GPU 1: ResNet50 (1.5h) → EfficientNetB1 (1.5h)
GPU 2: EfficientNetB0 (1.0h) → Wait
─────────────────────────────
TOTAL: 3.0 hours
```

**Option 2:** Train fastest 2, then slowest
```
GPU 1: EfficientNetB0 (1.0h) → ResNet50 (1.5h)
GPU 2: EfficientNetB1 (1.5h)
─────────────────────────────
TOTAL: 2.5 hours
```

---

## 📈 Detailed Breakdown

### **ResNet50 (50 epochs total)**

#### GPU Training:
```
Phase 1 (25 epochs, frozen base):
- Time per epoch: ~1.8 minutes
- Total: 25 × 1.8 = 45 minutes

Phase 2 (25 epochs, fine-tuning):
- Time per epoch: ~2.0 minutes (slower due to more trainable params)
- Total: 25 × 2.0 = 50 minutes

TOTAL: 95 minutes ≈ 1.5 hours
```

#### CPU Training:
```
Phase 1: 25 × 7 min = 175 min ≈ 3 hours
Phase 2: 25 × 8.5 min = 212 min ≈ 3.5 hours
TOTAL: 6.5 hours
```

---

### **EfficientNetB0 (50 epochs total)**

#### GPU Training:
```
Phase 1 (25 epochs):
- Time per epoch: ~1.2 minutes
- Total: 25 × 1.2 = 30 minutes

Phase 2 (25 epochs):
- Time per epoch: ~1.4 minutes
- Total: 25 × 1.4 = 35 minutes

TOTAL: 65 minutes ≈ 1 hour
```

#### CPU Training:
```
Phase 1: 25 × 5 min = 125 min ≈ 2 hours
Phase 2: 25 × 6 min = 150 min ≈ 2.5 hours
TOTAL: 4.5 hours
```

---

### **EfficientNetB1 (60 epochs total)**

#### GPU Training:
```
Phase 1 (30 epochs):
- Time per epoch: ~1.5 minutes
- Total: 30 × 1.5 = 45 minutes

Phase 2 (30 epochs):
- Time per epoch: ~1.7 minutes
- Total: 30 × 1.7 = 51 minutes

TOTAL: 96 minutes ≈ 1.5 hours
```

#### CPU Training:
```
Phase 1: 30 × 6 min = 180 min ≈ 3 hours
Phase 2: 30 × 7 min = 210 min ≈ 3.5 hours
TOTAL: 6.5 hours
```

---

## 💡 Quick Test Mode

If you want to test quickly (10 epochs per model):

### GPU:
```
ResNet50:        ~20 minutes
EfficientNetB0:  ~15 minutes
EfficientNetB1:  ~20 minutes
─────────────────────────────
TOTAL:           ~55 minutes
```

### CPU:
```
ResNet50:        ~1.5 hours
EfficientNetB0:  ~1 hour
EfficientNetB1:  ~1.5 hours
─────────────────────────────
TOTAL:           ~4 hours
```

**Command:**
```bash
python model_training/fracatlas/train_all.py --quick
```

---

## 🎯 Recommendations

### **If you have GPU:**
✅ **Train all models sequentially:** 4 hours  
✅ **Best time:** Overnight or during work hours  
✅ **Expected:** High accuracy (94-95%)

### **If you have CPU only:**
✅ **Train all models sequentially:** 17-18 hours  
✅ **Best time:** Overnight (start before sleep)  
✅ **Expected:** Same accuracy, just slower

### **If you have multiple GPUs:**
✅ **Train in parallel:** 1.5-2.5 hours  
✅ **Massive time savings**  
✅ **Requires GPU configuration**

---

## ⚡ Speed Optimization Tips

### **1. Reduce Batch Size (if memory issues):**
```python
# Current
batch_size = 32  # ResNet50, EfficientNetB0
batch_size = 16  # EfficientNetB1

# Smaller (slower but less memory)
batch_size = 16  # All models
batch_size = 8   # Very limited memory
```

### **2. Mixed Precision Training (GPU only):**
```python
# Add to training
tf.keras.mixed_precision.set_global_policy('mixed_float16')
# Speed increase: 20-30%
```

### **3. Reduce Epochs (for testing):**
```python
# Quick test
epochs = 10  # ~1 hour GPU, ~4 hours CPU

# Moderate
epochs = 30  # ~2.5 hours GPU, ~10 hours CPU

# Full training
epochs = 50  # ~4 hours GPU, ~17 hours CPU
```

### **4. Use Smaller Input Size:**
```python
# Current
input_size = 224  # ResNet50, EfficientNetB0
input_size = 240  # EfficientNetB1

# Smaller (faster but may reduce accuracy)
input_size = 192  # All models
# Speed increase: 15-20%
# Accuracy decrease: 1-2%
```

---

## 📊 Time vs Accuracy Trade-off

| Epochs | GPU Time | CPU Time | Expected Accuracy |
|--------|----------|----------|-------------------|
| 10 (quick) | 1 hour | 4 hours | 90-92% |
| 30 (moderate) | 2.5 hours | 10 hours | 93-94% |
| 50 (full) | 4 hours | 17 hours | 94-95% |
| 100 (extended) | 8 hours | 34 hours | 94.5-95.5% |

**Recommendation:** 50 epochs is optimal (good accuracy, reasonable time)

---

## 🕐 Training Schedule Suggestions

### **GPU Users:**

**Option 1: Morning Start**
```
9:00 AM  - Start training
1:00 PM  - Training complete (4 hours)
1:00 PM  - Review results
```

**Option 2: Overnight**
```
11:00 PM - Start training
3:00 AM  - Training complete (4 hours)
Morning  - Review results
```

### **CPU Users:**

**Option 1: Overnight (Recommended)**
```
10:00 PM - Start training
3:00 PM  - Training complete (17 hours)
Next day - Review results
```

**Option 2: Weekend**
```
Saturday 8:00 AM  - Start training
Sunday 1:00 AM    - Training complete
Sunday morning    - Review results
```

---

## 🎯 Summary Table

| Hardware | Sequential | Parallel (2 GPU) | Parallel (3 GPU) |
|----------|-----------|------------------|------------------|
| **GPU (RTX 3060)** | 4 hours | 2.5 hours | 1.5 hours |
| **CPU (i3 12th)** | 17 hours | N/A | N/A |
| **GPU (RTX 4090)** | 2.5 hours | 1.5 hours | 1 hour |
| **CPU (i7 13th)** | 12 hours | N/A | N/A |

---

## 💻 Your System Check

To check your hardware:

```python
import tensorflow as tf

# Check GPU
print("GPUs Available:", len(tf.config.list_physical_devices('GPU')))
print("GPU Details:", tf.config.list_physical_devices('GPU'))

# Check CPU
print("CPUs Available:", len(tf.config.list_physical_devices('CPU')))
```

---

## 🚀 Commands

### Train All Models (Sequential):
```bash
# Full training (50 epochs)
python model_training/fracatlas/train_all.py

# Quick test (10 epochs)
python model_training/fracatlas/train_all.py --quick

# Custom epochs
python model_training/fracatlas/train_all.py --epochs 30
```

### Train Individual Models:
```bash
# ResNet50 (~1.5h GPU, ~6.5h CPU)
python model_training/fracatlas/train_single.py --model resnet50

# EfficientNetB0 (~1h GPU, ~4.5h CPU)
python model_training/fracatlas/train_single.py --model efficientnet_b0

# EfficientNetB1 (~1.5h GPU, ~6.5h CPU)
python model_training/fracatlas/train_single.py --model efficientnet_b1
```

---

## ✅ Final Answer

### **Your Question: How much time?**

**Sequential Training (train_all.py):**
- **GPU:** 4 hours total
- **CPU:** 17 hours total

**Individual Models:**
- **ResNet50:** 1.5h (GPU) or 6.5h (CPU)
- **EfficientNetB0:** 1h (GPU) or 4.5h (CPU)
- **EfficientNetB1:** 1.5h (GPU) or 6.5h (CPU)

**Parallel Training (if 3 GPUs):**
- **All at once:** 1.5 hours

---

**Recommendation:** Use GPU if available, train overnight on CPU if not. 🚀
