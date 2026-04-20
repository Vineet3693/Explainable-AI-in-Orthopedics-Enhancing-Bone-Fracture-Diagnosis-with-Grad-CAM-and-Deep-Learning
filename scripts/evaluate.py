"""
Model evaluation script with comprehensive metrics

PURPOSE:
    Evaluates trained models on test set with medical AI specific metrics.
    Generates detailed reports including confusion matrix, ROC curve,
    and per-class performance analysis.

USAGE:
    python scripts/evaluate.py --model models/resnet50_final.h5 --data data/test

METRICS CALCULATED:
    - Accuracy, Precision, Recall, F1-Score
    - Sensitivity, Specificity (medical AI metrics)
    - False Negative Rate (critical for patient safety)
    - AUC-ROC
    - Confusion Matrix
    - Per-class performance

OUTPUT:
    - Console: Summary metrics
    - File: Detailed JSON report
    - Plots: Confusion matrix, ROC curve

EXAMPLE USE:
    python scripts/evaluate.py --model models/resnet50_final.h5
"""

import argparse
import os
import sys
from pathlib import Path
import yaml
import numpy as np
from tensorflow import keras
from src.data.dataset import FractureDataset
from src.evaluation.evaluator import Evaluator
import logging
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Evaluate fracture detection model')
    
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to trained model (.h5 file)'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/processed',
        help='Path to processed data directory'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='results/metrics/evaluation_results.json',
        help='Path to save evaluation results'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.5,
        help='Classification threshold'
    )
    
    return parser.parse_args()


def main():
    """Main evaluation function"""
    args = parse_args()
    
    logger.info("=" * 60)
    logger.info("Fracture Detection AI - Model Evaluation")
    logger.info("=" * 60)
    
    # Load model
    logger.info(f"Loading model from {args.model}")
    model = keras.models.load_model(args.model)
    
    # Load test dataset
    logger.info("Loading test dataset...")
    test_dataset = FractureDataset(
        data_dir=args.data_dir,
        split='test',
        image_size=(224, 224),
        batch_size=32
    )
    
    test_data = test_dataset.create_tf_dataset()
    
    logger.info(f"Test samples: {len(test_dataset)}")
    
    # Create evaluator
    evaluator = Evaluator(model)
    
    # Evaluate model
    logger.info("Evaluating model...")
    metrics = evaluator.evaluate(test_data, threshold=args.threshold)
    
    # Print results
    logger.info("\n" + "=" * 60)
    logger.info("Evaluation Results")
    logger.info("=" * 60)
    logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall (Sensitivity): {metrics['recall']:.4f}")
    logger.info(f"Specificity: {metrics['specificity']:.4f}")
    logger.info(f"F1-Score: {metrics['f1_score']:.4f}")
    logger.info(f"AUC-ROC: {metrics['auc_roc']:.4f}")
    logger.info(f"False Negative Rate: {metrics['false_negative_rate']:.4f}")
    logger.info(f"False Positive Rate: {metrics['false_positive_rate']:.4f}")
    
    logger.info("\nConfusion Matrix:")
    cm = np.array(metrics['confusion_matrix'])
    logger.info(f"TN: {cm[0][0]}, FP: {cm[0][1]}")
    logger.info(f"FN: {cm[1][0]}, TP: {cm[1][1]}")
    
    logger.info("\nClassification Report:")
    logger.info(metrics['classification_report'])
    
    # Save results
    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    with open(args.output, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    logger.info(f"\nResults saved to {args.output}")
    
    # Get misclassified samples
    fn_indices, fp_indices = evaluator.get_misclassified_samples(test_data, args.threshold)
    
    logger.info(f"\nMisclassified Samples:")
    logger.info(f"False Negatives: {len(fn_indices)}")
    logger.info(f"False Positives: {len(fp_indices)}")
    
    logger.info("\nEvaluation completed successfully!")


if __name__ == "__main__":
    main()
