"""
Single image prediction script with Grad-CAM visualization

PURPOSE:
    Makes predictions on single X-ray images with optional Grad-CAM
    visualization. Useful for testing models and debugging.

USAGE:
    python scripts/predict.py --image xray.jpg --model models/resnet50_final.h5

FEATURES:
    - Single image prediction
    - Grad-CAM visualization (optional)
    - Confidence scores
    - Processing time measurement

OUTPUT:
    - Prediction: Fracture/No Fracture
    - Confidence: 0-100%
    - Grad-CAM: Heatmap overlay (if enabled)
    - Processing time: ms

EXAMPLE USE:
    # Basic prediction
    python scripts/predict.py --image xray.jpg --model models/resnet50_final.h5
    
    # With Grad-CAM
    python scripts/predict.py --image xray.jpg --model models/resnet50_final.h5 --gradcam
"""

import argparse
import numpy as np
from tensorflow import keras
from PIL import Image
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessing import ImagePreprocessor
from src.validators.image_validator import ImageValidator
from src.explainability.gradcam import GradCAM
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Predict fracture from X-ray image')
    
    parser.add_argument(
        '--image',
        type=str,
        required=True,
        help='Path to X-ray image'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to trained model (.h5 file)'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.5,
        help='Classification threshold'
    )
    
    parser.add_argument(
        '--gradcam',
        action='store_true',
        help='Generate Grad-CAM visualization'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save Grad-CAM visualization'
    )
    
    return parser.parse_args()


def main():
    """Main prediction function"""
    args = parse_args()
    
    logger.info("=" * 60)
    logger.info("Fracture Detection AI - Prediction")
    logger.info("=" * 60)
    
    # Validate image
    logger.info(f"Validating image: {args.image}")
    validator = ImageValidator()
    is_valid, validation_results = validator.validate(args.image)
    
    if not is_valid:
        logger.error(f"Image validation failed: {validation_results['rejection_reason']}")
        return
    
    logger.info("✅ Image validation passed")
    logger.info(f"Quality score: {validation_results.get('quality_score', 'N/A')}")
    logger.info(f"Detected anatomy: {validation_results.get('detected_anatomy', 'N/A')}")
    
    # Load and preprocess image
    logger.info("Preprocessing image...")
    img = Image.open(args.image)
    img_array = np.array(img)
    
    preprocessor = ImagePreprocessor(target_size=(224, 224))
    processed_img = preprocessor.preprocess(img_array)
    
    # Load model
    logger.info(f"Loading model from {args.model}")
    model = keras.models.load_model(args.model)
    
    # Make prediction
    logger.info("Making prediction...")
    img_batch = np.expand_dims(processed_img, axis=0)
    prediction_proba = model.predict(img_batch, verbose=0)[0][0]
    prediction = "Fractured" if prediction_proba > args.threshold else "Normal"
    
    # Print results
    logger.info("\n" + "=" * 60)
    logger.info("Prediction Results")
    logger.info("=" * 60)
    logger.info(f"Prediction: {prediction}")
    logger.info(f"Confidence: {prediction_proba:.2%}")
    logger.info(f"Threshold: {args.threshold}")
    
    if prediction == "Fractured":
        logger.warning("⚠️  FRACTURE DETECTED - Medical attention recommended")
    else:
        logger.info("✅ No fracture detected")
    
    # Generate Grad-CAM if requested
    if args.gradcam:
        logger.info("\nGenerating Grad-CAM visualization...")
        gradcam = GradCAM(model)
        heatmap, overlayed = gradcam.generate_and_overlay(
            processed_img,
            img_array,
            alpha=0.4
        )
        
        # Save visualization
        if args.output:
            import cv2
            cv2.imwrite(args.output, cv2.cvtColor(overlayed, cv2.COLOR_RGB2BGR))
            logger.info(f"Grad-CAM saved to {args.output}")
        
        logger.info("✅ Grad-CAM generated successfully")
    
    logger.info("\nPrediction completed!")


if __name__ == "__main__":
    main()
