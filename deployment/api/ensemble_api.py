"""
FastAPI endpoint for ensemble predictions
Integrates with React frontend
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path
import tempfile
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ensemble.ensemble_predictor import FractureEnsemble

# Initialize FastAPI app
app = FastAPI(
    title="Fracture Detection API",
    description="Multi-model ensemble system for X-ray fracture detection",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],  # React and Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ensemble (loaded once at startup)
ensemble = None

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    global ensemble
    print("🚀 Loading ensemble models...")
    try:
        ensemble = FractureEnsemble()
        print("✅ Ensemble loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load ensemble: {str(e)}")
        print("⚠️ Make sure models are trained first!")


# Response models
class ModelPrediction(BaseModel):
    model: str
    confidence: float
    prediction: Optional[str] = None
    weight: Optional[float] = None
    accuracy: Optional[float] = None


class PredictionResponse(BaseModel):
    final_result: str
    final_confidence: float
    individual_predictions: List[ModelPrediction]
    recommendation: str
    methods_agree: Optional[bool] = None
    selected_model: Optional[str] = None  # name of the individual model requested (if any)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fracture Detection API",
        "status": "running",
        "models_loaded": ensemble is not None,
        "endpoints": {
            "/predict": "POST - Upload X-ray image for prediction",
            "/predict/voting": "POST - Voting ensemble prediction",
            "/predict/weighted": "POST - Weighted ensemble prediction",
            "/models": "GET - Get loaded models info",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": ensemble is not None,
        "total_models": len(ensemble.models) if ensemble else 0
    }


@app.get("/models")
async def get_models_info():
    """Get information about loaded models"""
    if ensemble is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    summary = ensemble.get_model_summary()
    # also indicate which model has the highest weight (best performance)
    best = None
    best_weight = 0
    for m in summary['models']:
        if m['weight'] > best_weight:
            best_weight = m['weight']
            best = m['name']
    if best:
        summary['best_model'] = best
    return summary


@app.post("/predict", response_model=PredictionResponse)
async def predict_fracture(file: UploadFile = File(...), model: Optional[str] = None):
    """
    Predict fracture from uploaded X-ray image
    If `model` query parameter is provided, run prediction using that single model.
    Otherwise perform the weighted ensemble (default best model behaviour).
    """
    if ensemble is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Train models first!")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Determine which prediction to run
        if model:
            # single model prediction
            if model not in ensemble.models:
                raise HTTPException(status_code=400, detail=f"Model '{model}' not available")
            single = ensemble.predict_individual(tmp_path, model)
            os.unlink(tmp_path)
            return {
                "final_result": single['prediction'],
                "final_confidence": single['confidence'],
                "individual_predictions": [single],
                "recommendation": ensemble._get_recommendation(single['prediction'], single['confidence'], True),
                "methods_agree": True,
                "selected_model": model
            }
        else:
            # weighted ensemble default behaviour
            result = ensemble.predict_all_methods(tmp_path)
            os.unlink(tmp_path)
            response = {
                "final_result": result['final_result'],
                "final_confidence": result['final_confidence'],
                "individual_predictions": result['weighted_ensemble']['individual_predictions'],
                "recommendation": result['recommendation'],
                "methods_agree": result['methods_agree'],
            }
            return response
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/voting")
async def predict_voting(file: UploadFile = File(...)):
    """
    Predict using voting ensemble
    Each model votes, majority wins
    """
    if ensemble is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        result = ensemble.predict_voting(tmp_path)
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/weighted")
async def predict_weighted(file: UploadFile = File(...)):
    """
    Predict using weighted ensemble
    Predictions weighted by model performance
    """
    if ensemble is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        result = ensemble.predict_weighted(tmp_path)
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/all")
async def predict_all_methods(file: UploadFile = File(...)):
    """
    Get predictions from all ensemble methods
    Returns voting, weighted, and combined results
    """
    if ensemble is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        result = ensemble.predict_all_methods(tmp_path)
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🏥 FRACTURE DETECTION API SERVER")
    print("=" * 80)
    print("\nStarting server...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop")
    print("=" * 80)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
