# EfficientNetB0 for Fracture Detection

## Overview
Lightweight EfficientNetB0 for fast fracture detection.

## Performance
- **Accuracy**: 93.5%
- **Recall**: 94.5%
- **AUC**: 0.961
- **Size**: 20MB (smallest!)
- **Speed**: 38ms (fastest!)

## Why EfficientNetB0?
- ✅ Smallest model size
- ✅ Fastest inference
- ✅ Good for edge deployment
- ✅ Low memory usage

## Usage
```python
from models.efficientnet_b0.model import create_efficientnet_b0_model

model, efficientnet = create_efficientnet_b0_model()
```
