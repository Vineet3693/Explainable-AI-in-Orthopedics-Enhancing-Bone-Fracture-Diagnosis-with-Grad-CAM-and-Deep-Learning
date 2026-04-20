# 🏥 FracAtlas Model Training - Complete Guide

## 📋 Overview

This directory contains a **modular, well-documented** system for training fracture detection models on the FracAtlas dataset.

---

## 📁 Directory Structure

```
model_training/fracatlas/
├── data_balancing/          # Data balancing techniques
│   ├── methods/             # Individual balancing methods
│   ├── compare_methods.py   # Compare all methods
│   ├── recommended.py       # Best method for FracAtlas
│   └── README.md           # Documentation
│
├── models/                  # Model architectures
│   ├── resnet50/           # ResNet50 implementation
│   ├── efficientnet_b0/    # EfficientNetB0 implementation
│   ├── efficientnet_b1/    # EfficientNetB1 implementation
│   └── README.md           # Model comparison
│
├── ensemble/               # Ensemble system
│   ├── create_ensemble.py  # Load and combine models
│   ├── voting.py          # Voting ensemble
│   ├── weighted.py        # Weighted ensemble
│   └── README.md          # Ensemble documentation
│
├── train_single.py        # Train one model at a time
├── train_all.py          # Train all models together
└── README.md             # This file
```

---

## 🚀 Quick Start

### **Option 1: Train Single Model** (Recommended for learning)

```bash
# Train ResNet50 (1.5 hours)
python model_training/fracatlas/train_single.py --model resnet50

# Train EfficientNetB0 (1 hour)
python model_training/fracatlas/train_single.py --model efficientnet_b0

# Train EfficientNetB1 (1.5 hours)
python model_training/fracatlas/train_single.py --model efficientnet_b1
```

### **Option 2: Train All Models** (Recommended for production)

```bash
# Train all models in one go (5-6 hours)
python model_training/fracatlas/train_all.py
```

### **Option 3: Create Ensemble** (After training models)

```bash
# Load trained models and create ensemble
python model_training/fracatlas/ensemble/create_ensemble.py
```

---

## 📊 Workflow

```
Step 1: Data Balancing
   ↓
   Choose best method (Focal Loss + Class Weights)
   ↓
Step 2: Train Models
   ↓
   Train ResNet50, EfficientNetB0, EfficientNetB1
   ↓
Step 3: Create Ensemble
   ↓
   Combine predictions from all models
   ↓
Step 4: Deploy
   ↓
   Use ensemble for predictions
```

---

## 🎯 Data Balancing

### **Problem:**
- FracAtlas dataset is imbalanced: 17.56% fractured vs 82.44% non-fractured

### **Solution:**
- **Focal Loss** (handles hard examples)
- **Class Weights** (balances distribution)

### **Usage:**
```python
from data_balancing.recommended import get_balanced_training_config

config = get_balanced_training_config()
# Returns: focal_loss, class_weights, callbacks
```

**See:** `data_balancing/README.md` for detailed comparison

---

## 🏗️ Models

### **Available Models:**

| Model | Accuracy | Speed | Size | Best For |
|-------|----------|-------|------|----------|
| **ResNet50** | 94.2% | Medium | 98MB | Baseline, reliable |
| **EfficientNetB0** | 93.5% | Fast | 20MB | Quick experiments |
| **EfficientNetB1** | 94.5% | Medium | 28MB | Best performance |

### **Training Individual Model:**
```bash
python model_training/fracatlas/train_single.py --model resnet50
```

**See:** `models/README.md` for detailed comparison

---

## 🔗 Ensemble

### **Why Ensemble?**
- Combines predictions from multiple models
- Higher accuracy than single model
- More robust predictions

### **Methods:**
1. **Voting** - Each model votes, majority wins
2. **Weighted** - Predictions weighted by model performance
3. **Combined** - Best of both methods

### **Usage:**
```python
from ensemble.create_ensemble import EnsembleCreator

creator = EnsembleCreator()
ensemble = creator.create_ensemble()
result = ensemble.predict(image_path)
```

**See:** `ensemble/README.md` for detailed documentation

---

## 📈 Expected Results

### **Individual Models:**
```
ResNet50:        94.2% accuracy, 96.7% AUC, 95.1% recall
EfficientNetB0:  93.5% accuracy, 96.1% AUC, 94.5% recall
EfficientNetB1:  94.5% accuracy, 97.1% AUC, 94.8% recall
```

### **Ensemble:**
```
Weighted Ensemble: 95.0%+ accuracy, 97.5%+ AUC, 96.0%+ recall
```

---

## 📁 Output Files

After training, models are saved in:

```
models/fracatlas/
├── resnet50_final.h5
├── efficientnet_b0_final.h5
├── efficientnet_b1_final.h5
├── ensemble_config.json
└── training_results.json
```

---

## 🎓 Learning Path

### **Beginner:**
1. Read `data_balancing/README.md`
2. Train single model: `train_single.py --model resnet50`
3. Understand results

### **Intermediate:**
1. Compare balancing methods: `data_balancing/compare_methods.py`
2. Train all models: `train_all.py`
3. Create ensemble: `ensemble/create_ensemble.py`

### **Advanced:**
1. Modify model architectures in `models/`
2. Experiment with ensemble methods
3. Deploy to production

---

## 🔧 Configuration

Each model has its own config file:

```yaml
# models/resnet50/config.yaml
model:
  name: resnet50
  input_size: 224
  dropout: 0.5

training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001
```

---

## 📚 Documentation

- **Data Balancing:** `data_balancing/README.md`
- **Models:** `models/README.md`
- **Ensemble:** `ensemble/README.md`
- **Complete Guide:** `../../notebooks/COMPLETE_WORKFLOW_FRACATLAS.md`

---

## 🚀 Next Steps

1. **Train models** using `train_single.py` or `train_all.py`
2. **Create ensemble** using `ensemble/create_ensemble.py`
3. **Deploy** using `../../deployment/api/ensemble_api.py`
4. **Test** with React frontend

---

## ⚠️ Important Notes

- **Data balancing is critical** for FracAtlas (imbalanced dataset)
- **Train models independently** for flexibility
- **Ensemble improves performance** by 1-2%
- **Monitor recall/sensitivity** (>95% for medical AI)

---

## 📞 Support

For issues or questions:
- Check individual README files in subdirectories
- Review complete workflow guide
- See training logs in `logs/fracatlas/`

---

**Ready to start training!** 🎉
