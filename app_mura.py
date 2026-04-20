"""
MURA Dataset Models - FastAPI Backend
Serves EfficientNetB0, EfficientNetB1, and VGG16 trained on MURA dataset
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
from fastapi.responses import FileResponse, JSONResponse
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────
app = FastAPI(
    title="Fracture Detection AI – MURA Models",
    description="Multi-model fracture detection using MURA-trained EfficientNetB0, EfficientNetB1 & VGG16",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# LLM Setup
# ──────────────────────────────────────────────
gemini_client = None
groq_client = None

def initialize_llms():
    global gemini_client, groq_client
    
    # Gemini
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            gemini_client = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini initialized")
        except Exception as e:
            print(f"⚠️ Gemini init failed: {e}")
    
    # Groq
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key:
        try:
            groq_client = Groq(api_key=groq_key)
            print("✅ Groq initialized")
        except Exception as e:
            print(f"⚠️ Groq init failed: {e}")

# ──────────────────────────────────────────────
# Model Registry  (name → path, metrics)
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "mura dataset kaggle results" / "models"

MODEL_REGISTRY = {
    "EfficientNetB0": {
        "path": MODEL_DIR / "EfficientNetB0.keras",
        "accuracy":  0.7216,
        "precision": 0.7356,
        "recall":    0.6529,
        "f1_score":  0.6918,
        "auc":       0.7931,
        "params":    "~4M",
        "input_size": 224,
    },
    "EfficientNetB1": {
        "path": MODEL_DIR / "EfficientNetB1.keras",
        "accuracy":  0.7163,
        "precision": 0.7498,
        "recall":    0.6111,
        "f1_score":  0.6734,
        "auc":       0.7751,
        "params":    "~6.5M",
        "input_size": 240,
    },
    "VGG16": {
        "path": MODEL_DIR / "VGG16.keras",
        "accuracy":  0.7701,
        "precision": 0.8177,
        "recall":    0.6686,
        "f1_score":  0.7357,
        "auc":       0.8366,
        "params":    "~138M",
        "input_size": 224,
    },
}

# Loaded tf.keras model objects
loaded_models: dict = {}

UPLOAD_DIR = BASE_DIR / "temp" / "mura_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# Startup – load all models
# ──────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 60)
    print("🏥  FRACTURE DETECTION AI  –  MURA MODELS")
    print("=" * 60)

    for name, meta in MODEL_REGISTRY.items():
        path = meta["path"]
        if path.exists():
            try:
                print(f"⏳ Loading {name} from {path} …")
                loaded_models[name] = tf.keras.models.load_model(str(path))
                print(f"   ✅ {name} loaded  (accuracy: {meta['accuracy']:.1%})")
            except Exception as exc:
                print(f"   ❌ Failed to load {name}: {exc}")
        else:
            print(f"   ⚠️  {name} – file not found: {path}")

    if not loaded_models:
        print("❌  No models loaded! Check the model directory.")
    else:
        print(f"\n✅  {len(loaded_models)}/{len(MODEL_REGISTRY)} models ready")
    
    print("\n🤖 Initializing LLM clients...")
    initialize_llms()
    print("=" * 60 + "\n")


# ──────────────────────────────────────────────
# Image Preprocessing
# ──────────────────────────────────────────────
def preprocess_image(model_name: str, image_path: str, target_size: int) -> np.ndarray:
    """Load, resize, and apply model-specific ImageNet preprocessing."""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((target_size, target_size))
    arr = np.array(img, dtype=np.float32)
    
    # Model specific preprocessing exactly as used in Kaggle training
    if "EfficientNet" in model_name:
        arr = tf.keras.applications.efficientnet.preprocess_input(arr)
    elif "VGG16" in model_name:
        arr = tf.keras.applications.vgg16.preprocess_input(arr)
        
    return np.expand_dims(arr, axis=0)


def run_single_model(name: str, image_path: str, threshold: float = 0.5) -> dict:
    """Run inference with one named model and return a result dict."""
    meta = MODEL_REGISTRY[name]
    img_array = preprocess_image(name, image_path, meta["input_size"])
    raw_score = float(loaded_models[name].predict(img_array, verbose=0)[0][0])
    
    # Sensitivity adjustment for specific models if needed
    is_fractured = raw_score > threshold
    
    confidence   = raw_score if is_fractured else 1.0 - raw_score
    return {
        "model":       name,
        "prediction":  "Fractured" if is_fractured else "Normal",
        "confidence":  round(confidence, 4),
        "raw_score":   round(raw_score, 4),
        "is_fractured": is_fractured,
        "metrics": {
            "accuracy":  meta["accuracy"],
            "precision": meta["precision"],
            "recall":    meta["recall"],
            "f1_score":  meta["f1_score"],
            "auc":       meta["auc"],
        }
    }


def run_ensemble(image_path: str) -> dict:
    """Average raw scores across all loaded models."""
    individual = []
    raw_scores  = []

    for name in loaded_models:
        res = run_single_model(name, image_path)
        individual.append(res)
        raw_scores.append(res["raw_score"])

    avg_score    = float(np.mean(raw_scores))
    is_fractured = avg_score > 0.5
    confidence   = avg_score if is_fractured else 1.0 - avg_score
    votes        = sum(1 for r in individual if r["is_fractured"])

    return {
        "final_result":    "Fractured" if is_fractured else "Normal",
        "final_confidence": round(confidence, 4),
        "avg_raw_score":   round(avg_score, 4),
        "votes_fractured": votes,
        "total_models":    len(individual),
        "methods_agree":   votes == 0 or votes == len(individual),
        "individual_predictions": individual,
        "recommendation": (
            "⚠️ URGENT: Fracture detected. Please consult an orthopedic specialist immediately."
            if is_fractured else
            "✅ No fracture detected. Monitor symptoms and follow up if pain persists."
        ),
    }


# ──────────────────────────────────────────────
# Explainability & AI Analysis
# ──────────────────────────────────────────────
def get_gradcam_heatmap(model, img_array, last_conv_layer_name, class_index=0):
    # Use model.inputs directly (not wrapped in extra list) to avoid tuple indexing error
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(last_conv_layer_name).output, model.output]
    )

    img_tensor = tf.cast(img_array, tf.float32)
    with tf.GradientTape() as tape:
        tape.watch(img_tensor)
        last_conv_layer_output, preds = grad_model(img_tensor)
        
        # Handle Keras 3 returning lists instead of raw tensors
        if isinstance(preds, list):
            preds = preds[0]
        if isinstance(last_conv_layer_output, list):
            last_conv_layer_output = last_conv_layer_output[0]
            
        # For binary sigmoid output
        class_channel = preds[:, 0]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)
    return heatmap.numpy()

def apply_heatmap(heatmap, image_path):
    img = cv2.imread(image_path)
    if img is None:
        # Fallback: read via PIL to handle more formats
        pil_img = Image.open(image_path).convert("RGB")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    # Ensure 3-channel BGR
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    superimposed_img = np.clip(heatmap_colored * 0.4 + img * 0.6, 0, 255).astype(np.uint8)

    output_path = UPLOAD_DIR / f"gradcam_{Path(image_path).name}"
    cv2.imwrite(str(output_path), superimposed_img)
    return str(output_path)

async def generate_ai_analysis(prediction_data: dict) -> dict:
    if not gemini_client and not groq_client:
        return {"error": "LLM services not configured"}

    analysis = {}
    
    if gemini_client:
        try:
            prompt = f"Medical AI Assistant Report:\nPrediction: {prediction_data['result']}\nConfidence: {prediction_data['confidence']:.1%}\nModel: {prediction_data['model']}\nProvide a detailed clinical analysis and recommendations."
            analysis['detailed'] = gemini_client.generate_content(prompt).text
        except Exception as e:
            analysis['detailed'] = f"Gemini Error: {str(e)}"

    if groq_client:
        try:
            # Use detailed if available, else just basic info
            source = analysis.get('detailed', f"Prediction: {prediction_data['result']} with {prediction_data['confidence']:.1%} confidence.")
            prompt = f"Summarize this into 3 concise bullet points:\n{source}"
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            analysis['summary'] = response.choices[0].message.content
        except Exception as e:
            analysis['summary'] = f"Groq Error: {str(e)}"
            
    return analysis


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Fracture Detection AI – MURA Models",
        "version": "2.0.0",
        "status":  "online",
        "models_loaded": list(loaded_models.keys()),
        "total_loaded":  len(loaded_models),
    }


@app.get("/health")
async def health():
    model_statuses = {
        name: "loaded" if name in loaded_models else "not_loaded"
        for name in MODEL_REGISTRY
    }
    return {
        "status":        "healthy" if loaded_models else "degraded",
        "models":        model_statuses,
        "total_loaded":  len(loaded_models),
        "timestamp":     datetime.now().isoformat(),
    }


@app.get("/api/v1/models")
async def get_models():
    """Return all available models with metrics."""
    models_list = []
    for name, meta in MODEL_REGISTRY.items():
        models_list.append({
            "name":       name,
            "status":     "active" if name in loaded_models else "not_loaded",
            "accuracy":   meta["accuracy"],
            "precision":  meta["precision"],
            "recall":     meta["recall"],
            "f1_score":   meta["f1_score"],
            "auc":        meta["auc"],
            "params":     meta["params"],
            "input_size": meta["input_size"],
        })
    return {
        "models":       models_list,
        "total_models": len(models_list),
        "loaded_count": len(loaded_models),
        "ensemble_available": len(loaded_models) > 1,
        "dataset":      "MURA (Musculoskeletal Radiographs)",
        "best_model":   "VGG16",
        "llm_enabled":  gemini_client is not None or groq_client is not None
    }

@app.get("/api/v1/roc-curve")
async def get_roc_curve():
    roc_path = BASE_DIR / "mura dataset kaggle results" / "plots" / "roc_curves.png"
    if roc_path.exists():
        return FileResponse(roc_path)
    raise HTTPException(status_code=404, detail="ROC curve image not found")


@app.post("/api/v1/predict")
async def predict(
    file: UploadFile = File(...),
    model_name: Optional[str] = Query(default=None, description="Model name or 'ensemble'"),
    sensitivity: str = Query(default="medium", description="high/medium/low sensitivity")
):
    """
    Predict fracture from an X-ray image.
    - model_name=None or 'ensemble' → weighted ensemble of all 3 models
    - model_name=EfficientNetB0 / EfficientNetB1 / VGG16 → single model
    """
    # Map sensitivity to threshold
    # High: 0.35 (Very aggressive), Medium: 0.45 (Sensitive), Low: 0.6 (Conservative)
    threshold_map = {"high": 0.35, "medium": 0.45, "low": 0.6}
    threshold = threshold_map.get(sensitivity.lower(), 0.45)

    if not loaded_models:
        raise HTTPException(status_code=503, detail="No models are loaded. Check server logs.")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    if model_name and model_name.lower() != "ensemble" and model_name not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model '{model_name}'. Available: {list(MODEL_REGISTRY.keys())}"
        )

    if model_name and model_name not in loaded_models and model_name.lower() != "ensemble":
        raise HTTPException(
            status_code=503,
            detail=f"Model '{model_name}' is registered but failed to load on startup."
        )

    # Save uploaded image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    fname     = f"{timestamp}_{file.filename}"
    fpath     = UPLOAD_DIR / fname

    try:
        with open(fpath, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        use_ensemble = (not model_name) or model_name.lower() == "ensemble"

        if use_ensemble:
            result = run_ensemble(str(fpath))
            result["mode"] = "ensemble"
        else:
            single = run_single_model(model_name, str(fpath), threshold=threshold)
            result = {
                "final_result":     single["prediction"],
                "final_confidence": single["confidence"],
                "avg_raw_score":    single["raw_score"],
                "votes_fractured":  1 if single["is_fractured"] else 0,
                "total_models":     1,
                "methods_agree":    True,
                "individual_predictions": [single],
                "recommendation": (
                    "⚠️ URGENT: Fracture detected. Please consult an orthopedic specialist immediately."
                    if single["is_fractured"] else
                    "✅ No fracture detected. Monitor symptoms and follow up if pain persists."
                ),
                "mode": "single",
                "selected_model": model_name,
            }

        # Add AI analysis if VGG16 (presentation focus) or specifically requested
        if (model_name == "VGG16" or use_ensemble) and fpath.exists():
            result["ai_analysis"] = await generate_ai_analysis({
                "result": result["final_result"],
                "confidence": result["final_confidence"],
                "model": model_name or "Ensemble"
            })
            
            # AUTOMATIC GRAD-CAM for VGG16
            if "VGG16" in loaded_models:
                try:
                    gc_img_array = preprocess_image("VGG16", str(fpath), 224)
                    heatmap = get_gradcam_heatmap(loaded_models["VGG16"], gc_img_array, "block5_conv3")
                    gc_path = apply_heatmap(heatmap, str(fpath))
                    # Return the filename so the frontend can fetch it
                    result["gradcam_image"] = f"/api/v1/temp/{Path(gc_path).name}"
                except Exception as e:
                    print(f"Auto Grad-CAM Failed: {e}")

        result["timestamp"] = datetime.now().isoformat()
        result["filename"]  = file.filename
        return result

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(exc)}")

    finally:
        # Keep file if we need it for Grad-CAM (separate request usually, but let's see)
        # For presentation, we might want a combined endpoint or just delete it.
        # We'll delete it for now to stay clean.
        if fpath.exists():
            fpath.unlink()

@app.post("/api/v1/gradcam")
async def gradcam_predict(file: UploadFile = File(...)):
    """Generate Grad-CAM heatmap for VGG16 model."""
    if "VGG16" not in loaded_models:
        raise HTTPException(status_code=503, detail="VGG16 model not loaded")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    fname = f"gc_{timestamp}_{file.filename}"
    fpath = UPLOAD_DIR / fname

    try:
        content = await file.read()
        with open(fpath, "wb") as buf:
            buf.write(content)

        img_array = preprocess_image("VGG16", str(fpath), 224)
        
        # Use predict class to determine focus
        raw_score = float(loaded_models["VGG16"].predict(img_array, verbose=0)[0][0])
        # If fractured, focus on abnormal. If normal, focus on what looks 'most abnormal' anyway
        heatmap = get_gradcam_heatmap(loaded_models["VGG16"], img_array, "block5_conv3", class_index=0)

        output_path = apply_heatmap(heatmap, str(fpath))
        
        # Save a copy that doesn't get unlinked for the frontend to fetch if needed
        return FileResponse(output_path, media_type="image/jpeg", filename=f"gradcam_{file.filename}")

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Grad-CAM failed: {str(exc)}")
    finally:
        if fpath.exists(): fpath.unlink()


@app.get("/api/v1/temp/{filename}")
async def get_temp_file(filename: str):
    fpath = UPLOAD_DIR / filename
    if fpath.exists():
        # Option to exclude files if they are just uploaded raw images (privacy)
        return FileResponse(fpath)
    raise HTTPException(status_code=404, detail="File not found")

# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🏥  MURA FRACTURE DETECTION API")
    print("=" * 60)
    print("  API:  http://localhost:8001")
    print("  Docs: http://localhost:8001/docs")
    print("=" * 60 + "\n")
    uvicorn.run("app_mura:app", host="0.0.0.0", port=8001, reload=False)
