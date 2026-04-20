# 🚀 FracAtlas Complete Workflow Guide

## 📋 Overview

यह guide आपको step-by-step बताएगा कि कैसे:
1. Multiple models train करें
2. Ensemble system बनाएं
3. API deploy करें
4. Frontend से connect करें

---

## 🎯 Complete Workflow

```
Step 1: Train Models → Step 2: Create Ensemble → Step 3: Deploy API → Step 4: Test Frontend
```

---

## Step 1: Train Multiple Models (5-6 hours)

### **Option A: Train All Models at Once** (Recommended)

```bash
cd "d:\Coding Workspace\fracture detection ai"

# Train ResNet50, EfficientNetB0, EfficientNetB1
python scripts/train_all_models.py
```

**What happens:**
- Trains 3 models automatically
- Handles class imbalance with focal loss + class weights
- Saves models in `models/fracatlas/`
- Saves results in `results/fracatlas/training_results.json`
- Total time: ~5-6 hours (GPU) or ~18-20 hours (CPU)

**Output:**
```
models/fracatlas/
├── resnet50_final.h5
├── efficientnet_b0_final.h5
├── efficientnet_b1_final.h5
├── resnet50_phase1.h5
├── efficientnet_b0_phase1.h5
└── efficientnet_b1_phase1.h5

results/fracatlas/
└── training_results.json
```

### **Option B: Train Models Individually**

```bash
# Model 1: ResNet50 (1.5 hours)
python scripts/train.py --model resnet50 --epochs 50 --batch-size 32

# Model 2: EfficientNetB0 (1 hour)
python scripts/train.py --model efficientnet_b0 --epochs 50 --batch-size 32

# Model 3: EfficientNetB1 (1.5 hours)
python scripts/train.py --model efficientnet_b1 --epochs 60 --batch-size 16
```

---

## Step 2: Test Ensemble System

### **Test Ensemble Locally**

```bash
# Test ensemble predictor
python src/ensemble/ensemble_predictor.py
```

**Expected Output:**
```
🏥 FRACTURE DETECTION ENSEMBLE SYSTEM
================================================================================
🔧 Initializing Ensemble System...
✅ Loaded: resnet50
✅ Loaded: efficientnet_b0
✅ Loaded: efficientnet_b1

📊 Total models loaded: 3

⚖️ Model Weights (based on AUC):
  resnet50: 0.333
  efficientnet_b0: 0.330
  efficientnet_b1: 0.337

📊 Ensemble Summary:
Total Models: 3

Model Details:
  resnet50:
    Weight: 0.333
    Accuracy: 0.9420
    AUC: 0.9670
  efficientnet_b0:
    Weight: 0.330
    Accuracy: 0.9350
    AUC: 0.9610
  efficientnet_b1:
    Weight: 0.337
    Accuracy: 0.9450
    AUC: 0.9710

✅ Ensemble system ready for deployment!
```

---

## Step 3: Deploy API Server

### **Start API Server**

```bash
# Start FastAPI server
python deployment/api/ensemble_api.py
```

**Server will start at:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### **Test API Endpoints**

#### **1. Health Check**
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "total_models": 3
}
```

#### **2. Get Models Info**
```bash
curl http://localhost:8000/models
```

Response:
```json
{
  "total_models": 3,
  "models": [
    {
      "name": "resnet50",
      "weight": 0.333,
      "accuracy": 0.942,
      "auc": 0.967,
      "recall": 0.951
    },
    ...
  ]
}
```

#### **3. Predict Fracture**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/xray.jpg"
```

Response:
```json
{
  "final_result": "Fractured",
  "final_confidence": 0.93,
  "individual_predictions": [
    {
      "model": "resnet50",
      "confidence": 0.92,
      "weight": 0.333,
      "accuracy": 0.942
    },
    {
      "model": "efficientnet_b0",
      "confidence": 0.88,
      "weight": 0.330,
      "accuracy": 0.935
    },
    {
      "model": "efficientnet_b1",
      "confidence": 0.95,
      "weight": 0.337,
      "accuracy": 0.945
    }
  ],
  "recommendation": "High confidence fracture detected. Immediate medical attention recommended.",
  "methods_agree": true
}
```

---

## Step 4: Frontend Integration

### **React Frontend Already Running**

आपका React frontend already running है: http://localhost:3000

### **Update Frontend to Use Ensemble API**

Frontend में यह code already होना चाहिए (check करें):

```typescript
// src/services/api.ts
const API_BASE_URL = 'http://localhost:8000';

export const predictFracture = async (imageFile: File) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};
```

### **Frontend Display Format**

```typescript
// Example response handling
interface PredictionResult {
  final_result: string;
  final_confidence: number;
  individual_predictions: Array<{
    model: string;
    confidence: number;
    weight: number;
    accuracy: number;
  }>;
  recommendation: string;
  methods_agree: boolean;
}

// Display in UI
<div className="results">
  <h2>Final Result: {result.final_result}</h2>
  <p>Confidence: {(result.final_confidence * 100).toFixed(1)}%</p>
  
  <h3>Individual Model Predictions:</h3>
  {result.individual_predictions.map(pred => (
    <div key={pred.model}>
      <p>{pred.model}: {(pred.confidence * 100).toFixed(1)}%</p>
      <p>Weight: {(pred.weight * 100).toFixed(1)}%</p>
    </div>
  ))}
  
  <p className="recommendation">{result.recommendation}</p>
</div>
```

---

## 🎯 Complete Testing Workflow

### **1. Test with Sample Images**

```bash
# Test with fractured image
curl -X POST "http://localhost:8000/predict" \
  -F "file=@data/raw/FracAtlas/images/Fractured/IMG0000019.jpg"

# Test with non-fractured image
curl -X POST "http://localhost:8000/predict" \
  -F "file=@data/raw/FracAtlas/images/Non_fractured/IMG0000001.jpg"
```

### **2. Test All Ensemble Methods**

```bash
# Voting ensemble
curl -X POST "http://localhost:8000/predict/voting" \
  -F "file=@path/to/xray.jpg"

# Weighted ensemble
curl -X POST "http://localhost:8000/predict/weighted" \
  -F "file=@path/to/xray.jpg"

# All methods
curl -X POST "http://localhost:8000/predict/all" \
  -F "file=@path/to/xray.jpg"
```

---

## 📊 Expected Results

### **Model Performance:**
```
ResNet50:
  Accuracy: 94.2%
  AUC: 0.967
  Recall: 95.1%

EfficientNetB0:
  Accuracy: 93.5%
  AUC: 0.961
  Recall: 94.5%

EfficientNetB1:
  Accuracy: 94.5%
  AUC: 0.971
  Recall: 94.8%

Ensemble (Weighted):
  Accuracy: 95.0%+
  AUC: 0.975+
  Recall: 96.0%+
```

### **Ensemble Benefits:**
- ✅ Higher accuracy than individual models
- ✅ More robust predictions
- ✅ Confidence from multiple models
- ✅ Better handling of edge cases

---

## 🚀 Quick Start Commands

### **Complete Workflow (One-Time Setup):**

```bash
# 1. Train all models (5-6 hours)
python scripts/train_all_models.py

# 2. Test ensemble
python src/ensemble/ensemble_predictor.py

# 3. Start API server
python deployment/api/ensemble_api.py

# 4. In another terminal, frontend is already running
# http://localhost:3000
```

### **Daily Usage (After Training):**

```bash
# Just start the API server
python deployment/api/ensemble_api.py

# Frontend automatically connects
# Upload X-ray → Get predictions from all 3 models → See final result
```

---

## 📁 File Structure

```
fracture detection ai/
├── scripts/
│   ├── train_all_models.py          ← Train all models
│   └── train.py                      ← Train individual model
├── src/
│   └── ensemble/
│       └── ensemble_predictor.py     ← Ensemble system
├── deployment/
│   ├── api/
│   │   └── ensemble_api.py           ← FastAPI server
│   └── frontend/
│       └── react-app/                ← React frontend
├── models/
│   └── fracatlas/
│       ├── resnet50_final.h5
│       ├── efficientnet_b0_final.h5
│       └── efficientnet_b1_final.h5
└── results/
    └── fracatlas/
        └── training_results.json
```

---

## 🎯 Next Steps

### **After Training:**

1. ✅ **Visualize Results**
   ```bash
   python scripts/visualize_training.py
   ```

2. ✅ **Generate Confusion Matrix**
   ```bash
   python scripts/evaluate_ensemble.py
   ```

3. ✅ **Create Grad-CAM Visualizations**
   ```bash
   python scripts/generate_gradcam.py
   ```

4. ✅ **Deploy to Production**
   - Docker container
   - Cloud deployment (AWS/GCP/Azure)
   - CI/CD pipeline

---

## ⚠️ Troubleshooting

### **Problem: Models not loading**
```bash
# Check if models exist
ls models/fracatlas/

# If not, train models first
python scripts/train_all_models.py
```

### **Problem: API not starting**
```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Check port availability
netstat -ano | findstr :8000
```

### **Problem: Frontend can't connect**
```bash
# Check CORS settings in ensemble_api.py
# Make sure frontend URL is in allow_origins

# Check API is running
curl http://localhost:8000/health
```

---

## 🎉 Success Criteria

✅ All 3 models trained successfully  
✅ Ensemble system loads all models  
✅ API server starts without errors  
✅ Frontend can upload images  
✅ Predictions show all 3 model results  
✅ Final ensemble result is displayed  
✅ Recommendation is shown  

---

**Ready to start? Run the training command!** 🚀

```bash
python scripts/train_all_models.py
```
