"""
FastAPI Application - Main API
Complete fracture detection API with LLM integration
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.inference.fracture_inference import FractureInferencePipeline
from src.monitoring.logging.structured_logger import setup_logging

# Initialize logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Fracture Detection AI",
    description="AI-powered fracture detection with LLM analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup"""
    global pipeline
    print("🚀 Starting Fracture Detection API...")
    pipeline = FractureInferencePipeline()
    print("✅ API ready!")

# Create upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "temp/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Response models
class PredictionResponse(BaseModel):
    prediction: dict
    explainability: dict
    analysis: dict
    model_info: dict
    status: str
    timestamp: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fracture Detection AI API",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "EfficientNetB0",
        "accuracy": 0.8409,
        "recall": 1.0,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/models")
async def get_models():
    """Get available models"""
    return {
        "models": [
            {
                "name": "EfficientNetB0",
                "status": "active",
                "accuracy": 0.8409,
                "recall": 1.0,
                "precision": 0.8409,
                "auc": 0.891,
                "f1_score": 0.9136
            }
        ],
        "ensemble_mode": "single",
        "total_models": 1
    }


@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_fracture(file: UploadFile = File(...)):
    """
    Predict fracture from X-ray image
    
    Complete workflow:
    1. Upload image
    2. Model prediction
    3. GradCAM heatmap
    4. Gemini analysis
    5. Groq summary
    6. Return results
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process image
        result = pipeline.process(str(file_path))
        
        # Add timestamp
        result['timestamp'] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        # Cleanup
        if file_path.exists():
            file_path.unlink()


@app.post("/api/v1/qa")
async def ask_question(question: str, context: Optional[str] = None):
    """
    Ask question about diagnosis
    Uses QA system
    """
    try:
        from src.qa_system.answer_generator import AnswerGenerator
        
        qa = AnswerGenerator()
        answer = qa.generate(question=question, context=context or "")
        
        return {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA failed: {str(e)}")


@app.post("/api/v1/feedback")
async def submit_feedback(
    prediction_id: str,
    feedback: str,
    correct: bool
):
    """Submit feedback on prediction"""
    try:
        from src.feedback.user_feedback_collector import collect_feedback
        
        feedback_data = {
            'prediction_id': prediction_id,
            'feedback': feedback,
            'correct': correct,
            'timestamp': datetime.now().isoformat()
        }
        
        collect_feedback(feedback_data)
        
        return {
            "status": "success",
            "message": "Feedback submitted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
