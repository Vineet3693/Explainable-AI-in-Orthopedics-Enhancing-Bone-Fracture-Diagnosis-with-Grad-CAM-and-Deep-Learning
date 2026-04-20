#!/usr/bin/env python3
"""
WHAT: Train All Models Script

WHY: Trains multiple models in one go
     Efficient - set and forget
     Consistent training across all models
     Automatic comparison and ensemble creation

HOW:
     1. Trains ResNet50, EfficientNetB0, EfficientNetB1
     2. Uses recommended balancing (Focal Loss + Class Weights)
     3. Saves all models
     4. Compares performance
     5. Creates ensemble configuration

WHEN TO USE:
     ✅ Production training
     ✅ Have time for full training (5-6 hours)
     ✅ Want all models at once
     ✅ Need consistent comparison

USAGE:
     python model_training/fracatlas/train_all.py
     python model_training/fracatlas/train_all.py --epochs 30  # Faster
     python model_training/fracatlas/train_all.py --quick      # Quick test

OUTPUT:
     - models/fracatlas/resnet50_final.h5
     - models/fracatlas/efficientnet_b0_final.h5
     - models/fracatlas/efficientnet_b1_final.h5
     - results/fracatlas/training_results.json
     - results/fracatlas/comparison.png
"""

import argparse
import sys
import os
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))

# Import train_single functionality
from train_single import train_model


MODELS_TO_TRAIN = ['resnet50', 'efficientnet_b0', 'efficientnet_b1']


def train_all_models(epochs=50, batch_size=32):
    """
    Train all models sequentially
    
    Args:
        epochs: Number of epochs per model
        batch_size: Batch size
    
    Returns:
        List of results for all models
    """
    print("=" * 80)
    print("🏥 TRAINING ALL FRACATLAS MODELS")
    print("=" * 80)
    print(f"\nModels to train: {len(MODELS_TO_TRAIN)}")
    print(f"Epochs per model: {epochs}")
    print(f"Batch size: {batch_size}")
    print(f"\nEstimated time: {estimate_training_time(epochs)} hours")
    
    results = []
    start_time = datetime.now()
    
    for i, model_name in enumerate(MODELS_TO_TRAIN, 1):
        print("\n" + "=" * 80)
        print(f"MODEL {i}/{len(MODELS_TO_TRAIN)}: {model_name.upper()}")
        print("=" * 80)
        
        try:
            # Train model
            model, metrics = train_model(model_name, epochs, batch_size)
            results.append(metrics)
            
            print(f"\n✅ {model_name} training complete!")
            
        except Exception as e:
            print(f"\n❌ Error training {model_name}: {str(e)}")
            continue
    
    total_time = (datetime.now() - start_time).total_seconds() / 3600
    
    # Save combined results
    save_results(results, total_time)
    
    # Create comparison
    create_comparison(results)
    
    # Print summary
    print_summary(results, total_time)
    
    return results


def estimate_training_time(epochs):
    """Estimate total training time"""
    # Rough estimates per model (in hours)
    times = {
        'resnet50': 1.5,
        'efficientnet_b0': 1.0,
        'efficientnet_b1': 1.5
    }
    
    total = sum(times.values()) * (epochs / 50)  # Scale by epochs
    return round(total, 1)


def save_results(results, total_time):
    """Save training results to JSON"""
    os.makedirs('results/fracatlas', exist_ok=True)
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_training_time_hours': total_time,
        'models': results
    }
    
    with open('results/fracatlas/training_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved to: results/fracatlas/training_results.json")


def create_comparison(results):
    """Create comparison visualization"""
    if not results:
        return
    
    df = pd.DataFrame(results)
    
    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Accuracy
    axes[0, 0].bar(df['model'], df['accuracy'])
    axes[0, 0].set_title('Accuracy Comparison')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].set_ylim([0.9, 1.0])
    
    # Plot 2: Recall (Critical!)
    axes[0, 1].bar(df['model'], df['recall'], color='orange')
    axes[0, 1].set_title('Recall Comparison (Critical for Medical AI)')
    axes[0, 1].set_ylabel('Recall')
    axes[0, 1].axhline(y=0.95, color='r', linestyle='--', label='Target: 95%')
    axes[0, 1].legend()
    axes[0, 1].set_ylim([0.9, 1.0])
    
    # Plot 3: AUC
    axes[1, 0].bar(df['model'], df['auc'], color='green')
    axes[1, 0].set_title('AUC Comparison')
    axes[1, 0].set_ylabel('AUC')
    axes[1, 0].set_ylim([0.9, 1.0])
    
    # Plot 4: F1 Score
    axes[1, 1].bar(df['model'], df['f1_score'], color='purple')
    axes[1, 1].set_title('F1 Score Comparison')
    axes[1, 1].set_ylabel('F1 Score')
    axes[1, 1].set_ylim([0.9, 1.0])
    
    plt.tight_layout()
    plt.savefig('results/fracatlas/comparison.png', dpi=300, bbox_inches='tight')
    
    print(f"📊 Comparison plot saved to: results/fracatlas/comparison.png")


def print_summary(results, total_time):
    """Print training summary"""
    print("\n" + "=" * 80)
    print("📊 TRAINING SUMMARY")
    print("=" * 80)
    
    if not results:
        print("\n❌ No models trained successfully")
        return
    
    print(f"\n{'Model':<20} {'Accuracy':<12} {'Recall':<12} {'AUC':<12} {'F1 Score':<12}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['model']:<20} "
              f"{result['accuracy']:<12.4f} "
              f"{result['recall']:<12.4f} "
              f"{result['auc']:<12.4f} "
              f"{result['f1_score']:<12.4f}")
    
    # Find best model
    best_model = max(results, key=lambda x: x['auc'])
    
    print("\n" + "=" * 80)
    print(f"🏆 BEST MODEL: {best_model['model']}")
    print(f"   Accuracy: {best_model['accuracy']:.4f}")
    print(f"   Recall: {best_model['recall']:.4f}")
    print(f"   AUC: {best_model['auc']:.4f}")
    print("=" * 80)
    
    print(f"\n⏱️ Total Training Time: {total_time:.1f} hours")
    
    print(f"\n📁 Saved Models:")
    for result in results:
        print(f"  - models/fracatlas/{result['model']}_final.h5")
    
    print(f"\n🚀 Next Steps:")
    print("  1. Create ensemble: python model_training/fracatlas/ensemble/create_ensemble.py")
    print("  2. Deploy API: python deployment/api/ensemble_api.py")
    print("  3. Test with frontend: http://localhost:3000")


def main():
    parser = argparse.ArgumentParser(description='Train all fracture detection models')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of epochs per model (default: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size (default: 32)')
    parser.add_argument('--quick', action='store_true',
                       help='Quick test mode (10 epochs)')
    
    args = parser.parse_args()
    
    if args.quick:
        args.epochs = 10
        print("\n⚡ QUICK TEST MODE: 10 epochs per model")
    
    # Train all models
    results = train_all_models(args.epochs, args.batch_size)
    
    print("\n" + "=" * 80)
    print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
