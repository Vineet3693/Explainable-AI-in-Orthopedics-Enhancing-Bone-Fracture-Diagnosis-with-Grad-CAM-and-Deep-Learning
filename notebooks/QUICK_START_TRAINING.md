# 🚀 Quick Start: Training FracAtlas Models

## 📊 Your Dataset Status
- **Total Images**: 4,083
- **Fractured**: 717 (17.56%) ⚠️ IMBALANCED!
- **Non-Fractured**: 3,366 (82.44%)
- **Status**: ✅ Ready for training

---

## 🎯 Recommended Models (Choose ONE)

### **Option 1: ResNet50** (Easiest, Most Reliable) ⭐
```bash
python scripts/train.py --model resnet50 --epochs 50 --batch-size 32
```
- **Time**: ~1.5 hours (GPU) / ~6 hours (CPU)
- **Accuracy**: ~94%
- **Best for**: First-time training, reliable baseline

### **Option 2: EfficientNetB0** (Fast, Lightweight)
```bash
python scripts/train.py --model efficientnet_b0 --epochs 50 --batch-size 32
```
- **Time**: ~1 hour (GPU) / ~4 hours (CPU)
- **Accuracy**: ~93%
- **Best for**: Quick experiments, limited hardware

### **Option 3: EfficientNetB1** (Best Balance)
```bash
python scripts/train.py --model efficientnet_b1 --epochs 60 --batch-size 16
```
- **Time**: ~1.5 hours (GPU) / ~5 hours (CPU)
- **Accuracy**: ~94-95%
- **Best for**: Production deployment

---

## ⚡ START TRAINING NOW!

### **Step 1: Choose Your Model**
I recommend starting with **ResNet50** for your first training run.

### **Step 2: Run Training Command**
```bash
cd "d:\Coding Workspace\fracture detection ai"
python scripts/train.py --model resnet50 --epochs 50 --batch-size 32
```

### **Step 3: Monitor Training**
The script will show:
- Training progress
- Validation accuracy
- Loss values
- Estimated time remaining

### **Step 4: Check Results**
After training, you'll find:
- **Model**: `models/checkpoints/resnet50_best.h5`
- **Final Model**: `models/final/resnet50_final.h5`
- **Logs**: `logs/resnet50/`

---

## 📋 Training Configuration

Your existing `configs/config.yaml` should include:

```yaml
# Model Configuration
model:
  architecture: resnet50
  freeze_layers: 100  # Freeze base layers initially
  dropout_rate: 0.5

# Data Configuration
data:
  image_size: 224
  batch_size: 32
  num_classes: 1  # Binary classification
  
# Training Configuration
training:
  epochs: 50
  optimizer: adam
  learning_rate: 0.001
  loss: binary_crossentropy  # Consider changing to focal_loss
  
  # Callbacks
  early_stopping_patience: 10
  reduce_lr_patience: 5
  reduce_lr_factor: 0.5
```

---

## ⚠️ IMPORTANT: Handle Imbalanced Data!

Your dataset is **highly imbalanced** (82% non-fractured). You MUST:

### **1. Use Class Weights** (Add to train.py)
```python
from sklearn.utils.class_weight import compute_class_weight

# Calculate class weights
class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = {0: class_weights[0], 1: class_weights[1]}

# Use in training
model.fit(..., class_weight=class_weight_dict)
```

### **2. Use Focal Loss** (Better than Binary Crossentropy)
Update `configs/config.yaml`:
```yaml
training:
  loss: focal_loss  # Instead of binary_crossentropy
  focal_alpha: 0.75
  focal_gamma: 2.0
```

### **3. Monitor Recall/Sensitivity** (Not just Accuracy!)
For medical AI, **Sensitivity > 95%** is critical (can't miss fractures!)

---

## 📊 Expected Results

### **After Training:**
```
Validation Accuracy:  ~94%
Validation AUC:       ~0.96
Sensitivity (Recall): ~95% (CRITICAL!)
Specificity:          ~93%
Training Time:        ~1.5 hours (GPU)
```

### **Warning Signs:**
- ❌ Accuracy > 98% → Probably overfitting
- ❌ Sensitivity < 90% → Missing too many fractures
- ❌ Large gap between train/val loss → Overfitting

---

## 🔧 Troubleshooting

### **Problem: Out of Memory**
```bash
# Reduce batch size
python scripts/train.py --model resnet50 --batch-size 16
```

### **Problem: Training Too Slow**
```bash
# Use smaller model
python scripts/train.py --model efficientnet_b0 --epochs 40
```

### **Problem: Low Accuracy**
- Check if data is preprocessed correctly
- Verify class weights are being used
- Try different learning rate (0.0001 instead of 0.001)
- Increase epochs (50 → 80)

---

## 📁 Files You Need

### **Already Exist:**
- ✅ `scripts/train.py` - Main training script
- ✅ `src/models/` - Model architectures
- ✅ `src/training/` - Training utilities
- ✅ `src/data/` - Data loaders
- ✅ `configs/config.yaml` - Configuration

### **Created for You:**
- ✅ `notebooks/FracAtlas_EDA_Analysis.ipynb` - EDA notebook
- ✅ `notebooks/run_fracatlas_eda.py` - EDA script
- ✅ `notebooks/TRAINING_GUIDE_FRACATLAS.md` - Detailed training guide
- ✅ `notebooks/fracatlas_eda_summary.txt` - Dataset summary

---

## 🎯 Recommended Training Workflow

### **Day 1: Quick Baseline**
```bash
# Train ResNet50 for quick baseline
python scripts/train.py --model resnet50 --epochs 30 --batch-size 32
```

### **Day 2: Optimize**
- Review results
- Adjust hyperparameters
- Add class weights
- Switch to focal loss

### **Day 3: Best Model**
```bash
# Train EfficientNetB1 with optimized settings
python scripts/train.py --model efficientnet_b1 --epochs 60 --batch-size 16
```

### **Day 4: Evaluate & Deploy**
- Generate confusion matrix
- Create Grad-CAM visualizations
- Test on validation samples
- Deploy to API

---

## 🚀 Ready to Start?

**Run this command now:**
```bash
cd "d:\Coding Workspace\fracture detection ai"
python scripts/train.py --model resnet50 --epochs 50 --batch-size 32
```

**Or for faster testing:**
```bash
python scripts/train.py --model efficientnet_b0 --epochs 30 --batch-size 32
```

---

## 📚 Additional Resources

- **Detailed Guide**: `notebooks/TRAINING_GUIDE_FRACATLAS.md`
- **Complete Guide**: `docs/guides/06-model-training-complete-guide.md`
- **Dataset Info**: `docs/guides/05-fracatlas-dataset-guide.md`
- **EDA Results**: `notebooks/fracatlas_eda_summary.txt`

---

**Good luck with training! 🎉**

The models are well-designed, the infrastructure is solid, and your dataset is ready. Just run the command and let it train!
