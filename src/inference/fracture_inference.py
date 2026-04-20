"""
Complete Inference Pipeline
Integrates trained model with LLM analysis
"""

import os
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, Any
from PIL import Image

from src.llm_integration.gemini_client import GeminiClient
from src.llm_integration.groq_client import GroqClient
from src.explainability.gradcam import GradCAM
from src.monitoring.logging.structured_logger import log_prediction


class FractureInferencePipeline:
    """Complete inference pipeline with LLM integration"""
    
    def __init__(self, model_path: str = None):
        """Initialize pipeline"""
        self.model_path = model_path or os.getenv('MODEL_PATH', 'models/fracatlas/efficientnet_b0_final.h5')
        
        # Load model
        print(f"Loading model from {self.model_path}...")
        self.model = tf.keras.models.load_model(self.model_path)
        print("✅ Model loaded successfully")
        
        # Initialize LLM clients
        self.gemini = GeminiClient()
        self.groq = GroqClient()
        
        # Initialize GradCAM
        self.gradcam = GradCAM(self.model)
        
        # Model info
        self.model_info = {
            'name': 'EfficientNetB0',
            'accuracy': 0.8409,
            'recall': 1.0,
            'precision': 0.8409,
            'auc': 0.891,
            'f1_score': 0.9136
        }
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for model"""
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """Make prediction"""
        # Preprocess
        img_array = self.preprocess_image(image_path)
        
        # Predict
        prediction_score = self.model.predict(img_array, verbose=0)[0][0]
        
        # Determine result
        is_fractured = prediction_score > 0.5
        confidence = float(prediction_score if is_fractured else 1 - prediction_score)
        
        return {
            'prediction': 'Fractured' if is_fractured else 'Non-Fractured',
            'confidence': confidence,
            'raw_score': float(prediction_score),
            'model': self.model_info['name'],
            'metrics': self.model_info
        }
    
    def generate_heatmap(self, image_path: str) -> str:
        """Generate GradCAM heatmap"""
        try:
            heatmap = self.gradcam.generate_heatmap(image_path)
            return heatmap
        except Exception as e:
            print(f"GradCAM failed: {e}")
            return None
    
    def analyze_with_gemini(self, prediction: Dict, image_path: str) -> str:
        """Generate detailed analysis with Gemini"""
        # Load prompt
        prompt_path = 'prompts_library/gemini_prompts/fracture_analysis.txt'
        
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
        else:
            prompt_template = """
            Analyze this X-ray fracture detection result:
            
            Prediction: {prediction}
            Confidence: {confidence:.2%}
            Model: {model}
            
            Provide a detailed medical analysis including:
            1. Assessment of the prediction
            2. Key findings
            3. Recommendations
            4. Differential diagnosis if applicable
            """
        
        prompt = prompt_template.format(
            prediction=prediction['prediction'],
            confidence=prediction['confidence'],
            model=prediction['model']
        )
        
        try:
            analysis = self.gemini.generate_text(prompt)
            return analysis
        except Exception as e:
            return f"Gemini analysis unavailable: {str(e)}"
    
    def summarize_with_groq(self, gemini_analysis: str) -> str:
        """Generate quick summary with Groq"""
        # Load prompt
        prompt_path = 'prompts_library/groq_prompts/quick_analysis.txt'
        
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
        else:
            prompt_template = """
            Summarize this medical analysis in 3-5 bullet points:
            
            {analysis}
            
            Focus on:
            - Key findings
            - Immediate actions
            - Critical information
            """
        
        prompt = prompt_template.format(analysis=gemini_analysis)
        
        try:
            summary = self.groq.generate_text(prompt)
            return summary
        except Exception as e:
            return f"Groq summary unavailable: {str(e)}"
    
    def process(self, image_path: str) -> Dict[str, Any]:
        """Complete processing pipeline"""
        print(f"\n🔍 Processing: {image_path}")
        
        # 1. Prediction
        print("1️⃣ Making prediction...")
        prediction = self.predict(image_path)
        print(f"   Result: {prediction['prediction']} ({prediction['confidence']:.2%})")
        
        # 2. Explainability
        print("2️⃣ Generating heatmap...")
        heatmap = self.generate_heatmap(image_path)
        
        # 3. Gemini analysis
        print("3️⃣ Generating Gemini analysis...")
        gemini_analysis = self.analyze_with_gemini(prediction, image_path)
        
        # 4. Groq summary
        print("4️⃣ Generating Groq summary...")
        groq_summary = self.summarize_with_groq(gemini_analysis)
        
        # 5. Combine results
        result = {
            'prediction': prediction,
            'explainability': {
                'heatmap': heatmap,
                'method': 'GradCAM'
            },
            'analysis': {
                'detailed': gemini_analysis,
                'summary': groq_summary
            },
            'model_info': self.model_info,
            'status': 'success'
        }
        
        # Log
        log_prediction(result)
        
        print("✅ Processing complete!\n")
        
        return result


if __name__ == "__main__":
    # Test pipeline
    pipeline = FractureInferencePipeline()
    
    # Test with sample image
    test_image = "data/raw/FracAtlas/images/Fractured/IMG0000019.jpg"
    
    if os.path.exists(test_image):
        result = pipeline.process(test_image)
        print("\n📊 Result:")
        print(f"Prediction: {result['prediction']['prediction']}")
        print(f"Confidence: {result['prediction']['confidence']:.2%}")
    else:
        print(f"Test image not found: {test_image}")
