# 🚀 Complete Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Git

---

## Step 1: Environment Setup

### 1.1 Clone Repository (if needed)
```bash
cd "d:\Coding Workspace\fracture detection ai"
```

### 1.2 Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 1.3 Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Step 2: API Keys Configuration

### 2.1 Copy Environment Template
```bash
copy .env.example .env
```

### 2.2 Get API Keys

**Gemini API Key:**
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

**Groq API Key:**
1. Go to: https://console.groq.com/keys
2. Sign up/Login
3. Create new API key
4. Copy the key

### 2.3 Add Keys to .env
Open `.env` file and add your keys:
```env
GEMINI_API_KEY=your_actual_gemini_key_here
GROQ_API_KEY=your_actual_groq_key_here
```

---

## Step 3: Verify Model

### 3.1 Check Model File
```bash
# Model should be at:
models/fracatlas/efficientnet_b0_final.h5
```

### 3.2 If Model Missing
```bash
# Train the model first
py model_training/fracatlas/train_single.py --model efficientnet_b0 --epochs 50
```

---

## Step 4: Test Backend

### 4.1 Test Inference Pipeline
```bash
py src/inference/fracture_inference.py
```

Expected output:
```
Loading model from models/fracatlas/efficientnet_b0_final.h5...
✅ Model loaded successfully
```

### 4.2 Start API Server
```bash
cd src/api
py main_api.py
```

Expected output:
```
🚀 Starting Fracture Detection API...
✅ API ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4.3 Test API
Open browser: http://localhost:8000

You should see:
```json
{
  "message": "Fracture Detection AI API",
  "version": "1.0.0",
  "status": "online"
}
```

Test health endpoint: http://localhost:8000/health

---

## Step 5: Test with Sample Image

### 5.1 Using cURL
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -F "file=@data/raw/FracAtlas/images/Fractured/IMG0000019.jpg"
```

### 5.2 Using Python
```python
import requests

url = "http://localhost:8000/api/v1/predict"
files = {'file': open('test_xray.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

---

## Step 6: Frontend Setup (Optional)

### 6.1 Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 6.2 Configure Frontend
Edit `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
```

### 6.3 Start Frontend
```bash
npm start
```

Frontend will open at: http://localhost:3000

---

## Step 7: Complete Workflow Test

### 7.1 Upload X-ray
1. Open http://localhost:3000
2. Click "Upload X-ray Image"
3. Select an X-ray image
4. Click "Analyze"

### 7.2 View Results
You should see:
- ✅ Model prediction
- ✅ Confidence score
- ✅ GradCAM heatmap
- ✅ Gemini detailed analysis
- ✅ Groq quick summary
- ✅ Q&A option
- ✅ Metrics dashboard

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution:** Make sure `.env` file exists and contains your API key

### Issue: "Model not found"
**Solution:** Train the model first or check the path in `.env`

### Issue: "Port 8000 already in use"
**Solution:** Change port in `.env`:
```env
API_PORT=8001
```

### Issue: "CORS error"
**Solution:** Add frontend URL to `.env`:
```env
CORS_ORIGINS=http://localhost:3000
```

---

## Production Deployment

### 1. Update .env for Production
```env
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=https://your-domain.com
SECRET_KEY=generate-strong-secret-key
```

### 2. Use Production Server
```bash
gunicorn src.api.main_api:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 3. Deploy Frontend
```bash
cd frontend
npm run build
# Deploy build/ folder to hosting
```

---

## Quick Start Commands

```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Start API
cd src/api
py main_api.py

# 3. In new terminal - Start frontend
cd frontend
npm start

# 4. Open browser
# http://localhost:3000
```

---

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/health` | GET | Health check |
| `/api/v1/models` | GET | Get model info |
| `/api/v1/predict` | POST | Predict fracture |
| `/api/v1/qa` | POST | Ask question |
| `/api/v1/feedback` | POST | Submit feedback |

---

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Gemini API key | ✅ Yes |
| `GROQ_API_KEY` | Groq API key | ✅ Yes |
| `MODEL_PATH` | Path to model file | ✅ Yes |
| `API_PORT` | API server port | No (default: 8000) |
| `CORS_ORIGINS` | Allowed origins | No |

---

**You're all set! 🎉**
