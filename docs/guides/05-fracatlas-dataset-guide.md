# 📊 FracAtlas Dataset Documentation

## Overview

The **FracAtlas dataset** is included in this project for training and evaluating the fracture detection models.

---

## 📁 Dataset Structure

```
data/raw/FracAtlas/
├── images/
│   ├── Fractured/          # X-rays with fractures
│   └── Non_fractured/      # Normal X-rays
├── Annotations/            # Fracture annotations (bounding boxes, labels)
├── Utilities/              # Dataset utility scripts
└── dataset.csv             # Metadata (image IDs, labels, locations)
```

---

## 📊 Dataset Contents

### **Images Folder**
The dataset is organized into two categories:
- **Fractured/** - X-ray images containing bone fractures
- **Non_fractured/** - Normal X-ray images without fractures

### **Annotations Folder**
Contains:
- Bounding box coordinates for fracture locations
- Fracture type labels
- Anatomical location information
- Expert radiologist annotations

### **dataset.csv**
Metadata file containing:
- Image IDs
- Fracture/Normal labels
- Anatomical locations (wrist, ankle, hip, etc.)
- Fracture types
- Patient demographics (anonymized)

---

## 🎯 Usage in Project

### **Training Pipeline**
```python
from src.data.data_loader import FracAtlasDataLoader

# Load dataset
loader = FracAtlasDataLoader('data/raw/FracAtlas')
train_data, val_data, test_data = loader.load_splits(
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15
)

# Train model
for images, labels in train_data:
    model.train(images, labels)
```

### **Data Preprocessing**
```python
from src.data.preprocessing import preprocess_xray

# Preprocess images
preprocessed = preprocess_xray(
    image_path='data/raw/FracAtlas/images/Fractured/001.jpg',
    target_size=(224, 224),
    normalize=True
)
```

### **Data Augmentation**
```python
from src.data.augmentation import augment_xray

# Apply augmentation
augmented = augment_xray(
    image,
    rotation_range=15,
    zoom_range=0.1,
    horizontal_flip=True
)
```

---

## 📈 Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Images** | Check `images/` folder |
| **Fractured Cases** | In `Fractured/` subfolder |
| **Normal Cases** | In `Non_fractured/` subfolder |
| **Anatomical Locations** | Multiple (wrist, ankle, hip, shoulder, etc.) |
| **Image Format** | JPG/PNG |
| **Annotations** | Bounding boxes + labels |

---

## 🔧 Integration with Project

### **Files Using This Dataset**

1. **Data Loading**
   - `src/data/data_loader.py` - Loads images and labels
   - `src/data/dataset.py` - PyTorch/TensorFlow dataset classes

2. **Preprocessing**
   - `src/data/preprocessing.py` - Image preprocessing
   - `src/data/augmentation.py` - Data augmentation

3. **Training**
   - `src/training/train.py` - Model training
   - `src/training/callbacks.py` - Training callbacks

4. **Evaluation**
   - `src/evaluation/metrics_calculator.py` - Performance metrics
   - `src/evaluation/confusion_matrix.py` - Confusion matrix

---

## 🎓 Dataset Quality

### **Strengths**
- ✅ Expert radiologist annotations
- ✅ Multiple anatomical locations
- ✅ Diverse fracture types
- ✅ High-quality X-ray images
- ✅ Balanced dataset (fractured/normal)

### **Considerations**
- ⚠️ Dataset size (may need augmentation)
- ⚠️ Image resolution variability
- ⚠️ Anatomical location distribution

---

## 📝 Data Format

### **Image Files**
- **Format:** JPG, PNG
- **Resolution:** Variable (typically 512x512 to 2048x2048)
- **Color:** Grayscale (X-ray images)
- **Naming:** Sequential IDs (001.jpg, 002.jpg, etc.)

### **Annotations**
- **Format:** JSON or XML
- **Contents:**
  - Bounding box coordinates (x, y, width, height)
  - Fracture type label
  - Anatomical location
  - Confidence score (if available)

### **Metadata CSV**
```csv
image_id,label,anatomical_location,fracture_type,split
001,fractured,wrist,distal_radius,train
002,normal,ankle,none,train
003,fractured,hip,femoral_neck,val
...
```

---

## 🚀 Quick Start

### **1. Verify Dataset**
```bash
python scripts/verify_dataset.py --data-dir data/raw/FracAtlas
```

### **2. Explore Dataset**
```bash
python scripts/explore_dataset.py --data-dir data/raw/FracAtlas
```

### **3. Train Model**
```bash
python scripts/train_model.py \
    --data-dir data/raw/FracAtlas \
    --model resnet50 \
    --epochs 50
```

---

## 🔒 Data Privacy

### **HIPAA Compliance**
- ✅ All patient identifiers removed
- ✅ Images anonymized
- ✅ No PHI (Protected Health Information)
- ✅ Safe for research and development

### **Usage Guidelines**
- Use only for research and development
- Do not re-identify patients
- Follow institutional review board (IRB) guidelines
- Cite original dataset authors

---

## 📚 Citation

If you use the FracAtlas dataset, please cite:

```bibtex
@article{fracatlas2023,
  title={FracAtlas: A Dataset for Fracture Classification, Localization and Segmentation of Musculoskeletal Radiographs},
  author={[Authors]},
  journal={[Journal]},
  year={2023}
}
```

---

## 🔗 Additional Resources

- **Original Dataset:** [FracAtlas Repository]
- **Paper:** [FracAtlas Paper Link]
- **Documentation:** [Official Docs]
- **License:** [Dataset License]

---

## ⚠️ Important Notes

1. **Git Exclusion**
   - Dataset files are excluded from git (see `.gitignore`)
   - Large files not tracked in version control
   - Download separately if cloning repository

2. **Storage Requirements**
   - Dataset size: ~[X] GB
   - Ensure sufficient disk space
   - Consider cloud storage for large datasets

3. **Licensing**
   - Check original dataset license
   - Ensure compliance for clinical use
   - Attribution required

---

## 🛠️ Troubleshooting

### **Dataset Not Found**
```bash
# Check if dataset exists
ls data/raw/FracAtlas/

# If missing, download from source
# [Download instructions]
```

### **CSV Loading Error**
```python
# Use pandas to inspect CSV
import pandas as pd
df = pd.read_csv('data/raw/FracAtlas/dataset.csv')
print(df.head())
print(df.info())
```

### **Image Loading Error**
```python
# Verify image paths
from pathlib import Path
images = list(Path('data/raw/FracAtlas/images').rglob('*.jpg'))
print(f"Found {len(images)} images")
```

---

## 📞 Support

For dataset-related questions:
- Check original FracAtlas documentation
- Review `src/data/` module documentation
- See `scripts/` for dataset utilities

---

**Dataset is ready for use in training and evaluation!** 🚀
