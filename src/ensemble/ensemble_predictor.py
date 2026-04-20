#!/usr/bin/env python3
"""
Ensemble Model System for FracAtlas
Combines predictions from multiple trained models
"""

import os
import json
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import List, Dict, Tuple

class FractureEnsemble:
    """
    Ensemble system that combines multiple CNN models
    Supports: Voting, Weighted Average, and Stacking
    """
    
    def __init__(self, models_dir: str = 'models/fracatlas'):
        """
        Initialize ensemble with trained models
        
        Args:
            models_dir: Directory containing trained models
        """
        self.models_dir = models_dir
        self.models = {}
        self.model_weights = {}
        self.model_info = {}
        
        print("🔧 Initializing Ensemble System...")
        self._load_models()
        self._load_model_info()
    
    def _load_models(self):
        """Load all trained models"""
        model_files = {
            'resnet50': 'resnet50_final.h5',
            'efficientnet_b0': 'efficientnet_b0_final.h5',
            'efficientnet_b1': 'efficientnet_b1_final.h5'
        }
        
        for model_name, filename in model_files.items():
            model_path = os.path.join(self.models_dir, filename)
            
            if os.path.exists(model_path):
                try:
                    model = tf.keras.models.load_model(
                        model_path,
                        custom_objects={'loss_fn': self._focal_loss()}
                    )
                    self.models[model_name] = model
                    print(f"✅ Loaded: {model_name}")
                except Exception as e:
                    print(f"⚠️ Failed to load {model_name}: {str(e)}")
            else:
                print(f"⚠️ Model not found: {model_path}")
        
        if not self.models:
            raise ValueError("No models loaded! Train models first using train_all_models.py")
        
        print(f"\n📊 Total models loaded: {len(self.models)}")
    
    def _load_model_info(self):
        """Load model performance metrics"""
        results_file = 'results/fracatlas/training_results.json'
        
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            # Store info and calculate weights based on AUC
            total_auc = 0
            for result in results:
                model_name = result['model']
                if model_name in self.models:
                    self.model_info[model_name] = result
                    total_auc += result['auc']
            
            # Calculate normalized weights
            for model_name in self.model_info:
                auc = self.model_info[model_name]['auc']
                self.model_weights[model_name] = auc / total_auc
            
            print("\n⚖️ Model Weights (based on AUC):")
            for name, weight in self.model_weights.items():
                print(f"  {name}: {weight:.3f}")
        else:
            # Equal weights if no results file
            print("\n⚠️ No results file found, using equal weights")
            num_models = len(self.models)
            for model_name in self.models:
                self.model_weights[model_name] = 1.0 / num_models
    
    def _focal_loss(self, alpha=0.75, gamma=2.0):
        """Focal loss function for loading models"""
        def loss_fn(y_true, y_pred):
            epsilon = tf.keras.backend.epsilon()
            y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
            cross_entropy = -y_true * tf.math.log(y_pred) - (1 - y_true) * tf.math.log(1 - y_pred)
            weight = alpha * y_true + (1 - alpha) * (1 - y_true)
            focal_weight = weight * tf.pow(tf.abs(y_true - y_pred), gamma)
            loss = focal_weight * cross_entropy
            return tf.reduce_mean(loss)
        return loss_fn
    
    def preprocess_image(self, image_path: str, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """
        Preprocess image for prediction
        
        Args:
            image_path: Path to X-ray image
            target_size: Target image size
            
        Returns:
            Preprocessed image array
        """
        from tensorflow.keras.preprocessing import image
        
        # Load image
        img = image.load_img(image_path, target_size=target_size)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Normalize
        img_array = img_array / 255.0
        
        return img_array
    
    def predict_voting(self, image_path: str) -> Dict:
        """
        Voting ensemble: Each model votes, majority wins
        
        Args:
            image_path: Path to X-ray image
            
        Returns:
            Dictionary with predictions and final result
        """
        img = self.preprocess_image(image_path)
        
        predictions = []
        votes = {'Fractured': 0, 'Non-Fractured': 0}
        
        for model_name, model in self.models.items():
            pred = model.predict(img, verbose=0)[0][0]
            result = 'Fractured' if pred > 0.5 else 'Non-Fractured'
            
            predictions.append({
                'model': model_name,
                'confidence': float(pred),
                'prediction': result,
                'accuracy': self.model_info.get(model_name, {}).get('accuracy', 0.0)
            })
            
            votes[result] += 1
        
        # Majority voting
        final_result = 'Fractured' if votes['Fractured'] > votes['Non-Fractured'] else 'Non-Fractured'
        
        return {
            'method': 'voting',
            'individual_predictions': predictions,
            'votes': votes,
            'final_result': final_result,
            'confidence': votes[final_result] / len(self.models)
        }
    
    def predict_weighted(self, image_path: str) -> Dict:
        """
        Weighted ensemble: Predictions weighted by model performance
        
        Args:
            image_path: Path to X-ray image
            
        Returns:
            Dictionary with predictions and final result
        """
        img = self.preprocess_image(image_path)
        
        predictions = []
        weighted_sum = 0.0
        
        for model_name, model in self.models.items():
            pred = model.predict(img, verbose=0)[0][0]
            weight = self.model_weights.get(model_name, 1.0 / len(self.models))
            
            predictions.append({
                'model': model_name,
                'confidence': float(pred),
                'weight': float(weight),
                'weighted_contribution': float(pred * weight),
                'accuracy': self.model_info.get(model_name, {}).get('accuracy', 0.0)
            })
            
            weighted_sum += pred * weight
        
        final_result = 'Fractured' if weighted_sum > 0.5 else 'Non-Fractured'
        
        return {
            'method': 'weighted',
            'individual_predictions': predictions,
            'final_confidence': float(weighted_sum),
            'final_result': final_result,
            'threshold': 0.5
        }

    def predict_individual(self, image_path: str, model_name: str) -> Dict:
        """
        Generate prediction using a single model from the ensemble.

        Args:
            image_path: Path to the X-ray image
            model_name: Key identifying which model to use (e.g. 'efficientnet_b0')

        Returns:
            Dictionary containing the single model's confidence and prediction.
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' is not loaded in the ensemble")

        img = self.preprocess_image(image_path)
        model = self.models[model_name]
        pred = model.predict(img, verbose=0)[0][0]
        result = 'Fractured' if pred > 0.5 else 'Non-Fractured'
        return {
            'model': model_name,
            'confidence': float(pred),
            'prediction': result,
            'accuracy': self.model_info.get(model_name, {}).get('accuracy', 0.0)
        }
    
    def predict_all_methods(self, image_path: str) -> Dict:
        """
        Get predictions from all ensemble methods
        
        Args:
            image_path: Path to X-ray image
            
        Returns:
            Dictionary with all predictions
        """
        voting_result = self.predict_voting(image_path)
        weighted_result = self.predict_weighted(image_path)
        
        # Determine final result (use weighted as primary)
        final_result = weighted_result['final_result']
        final_confidence = weighted_result['final_confidence']
        
        # Agreement check
        agreement = voting_result['final_result'] == weighted_result['final_result']
        
        return {
            'image_path': image_path,
            'voting_ensemble': voting_result,
            'weighted_ensemble': weighted_result,
            'final_result': final_result,
            'final_confidence': final_confidence,
            'methods_agree': agreement,
            'recommendation': self._get_recommendation(final_result, final_confidence, agreement)
        }
    
    def _get_recommendation(self, result: str, confidence: float, agreement: bool) -> str:
        """Generate medical recommendation based on prediction"""
        if result == 'Fractured':
            if confidence > 0.9 and agreement:
                return "High confidence fracture detected. Immediate medical attention recommended."
            elif confidence > 0.7:
                return "Fracture likely detected. Medical consultation recommended."
            else:
                return "Possible fracture detected. Further examination recommended."
        else:
            if confidence < 0.3 and not agreement:
                return "Uncertain result. Additional imaging or expert review recommended."
            elif confidence < 0.5:
                return "Low confidence in non-fracture classification. Consider follow-up."
            else:
                return "No fracture detected. Routine follow-up as needed."
    
    def batch_predict(self, image_paths: List[str], method: str = 'weighted') -> List[Dict]:
        """
        Predict on multiple images
        
        Args:
            image_paths: List of image paths
            method: Ensemble method ('voting', 'weighted', or 'all')
            
        Returns:
            List of prediction results
        """
        results = []
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\nProcessing image {i}/{len(image_paths)}: {image_path}")
            
            try:
                if method == 'voting':
                    result = self.predict_voting(image_path)
                elif method == 'weighted':
                    result = self.predict_weighted(image_path)
                else:  # 'all'
                    result = self.predict_all_methods(image_path)
                
                results.append(result)
                print(f"✅ Result: {result.get('final_result', 'N/A')}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results.append({'error': str(e), 'image_path': image_path})
        
        return results
    
    def get_model_summary(self) -> Dict:
        """Get summary of loaded models"""
        summary = {
            'total_models': len(self.models),
            'models': []
        }
        
        for model_name in self.models:
            info = self.model_info.get(model_name, {})
            summary['models'].append({
                'name': model_name,
                'weight': self.model_weights.get(model_name, 0.0),
                'accuracy': info.get('accuracy', 0.0),
                'auc': info.get('auc', 0.0),
                'recall': info.get('recall', 0.0)
            })
        
        return summary


def main():
    """Demo usage of ensemble system"""
    print("=" * 80)
    print("🏥 FRACTURE DETECTION ENSEMBLE SYSTEM")
    print("=" * 80)
    
    # Initialize ensemble
    ensemble = FractureEnsemble()
    
    # Print model summary
    summary = ensemble.get_model_summary()
    print(f"\n📊 Ensemble Summary:")
    print(f"Total Models: {summary['total_models']}")
    print(f"\nModel Details:")
    for model in summary['models']:
        print(f"  {model['name']}:")
        print(f"    Weight: {model['weight']:.3f}")
        print(f"    Accuracy: {model['accuracy']:.4f}")
        print(f"    AUC: {model['auc']:.4f}")
    
    # Example prediction (if test image exists)
    test_image = "data/raw/FracAtlas/images/Fractured/IMG0000019.jpg"
    
    if os.path.exists(test_image):
        print(f"\n🔍 Testing on sample image: {test_image}")
        result = ensemble.predict_all_methods(test_image)
        
        print(f"\n📊 Prediction Results:")
        print(f"Final Result: {result['final_result']}")
        print(f"Confidence: {result['final_confidence']:.4f}")
        print(f"Methods Agree: {result['methods_agree']}")
        print(f"\nRecommendation: {result['recommendation']}")
        
        print(f"\n📋 Individual Model Predictions:")
        for pred in result['weighted_ensemble']['individual_predictions']:
            print(f"  {pred['model']}: {pred['confidence']:.4f} (weight: {pred['weight']:.3f})")
    
    print("\n" + "=" * 80)
    print("✅ Ensemble system ready for deployment!")
    print("=" * 80)


if __name__ == "__main__":
    main()
