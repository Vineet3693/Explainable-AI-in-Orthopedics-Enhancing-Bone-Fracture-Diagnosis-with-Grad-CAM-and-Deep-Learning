"""
Main training script for fracture detection models

PURPOSE:
    Orchestrates end-to-end model training including data loading, model
    creation, training execution, and model saving. Command-line interface
    for easy experimentation with different configurations.

WHY DEDICATED TRAINING SCRIPT:
    Scattered training code: Hard to reproduce experiments
    Dedicated script: Consistent, reproducible, easy to use
    
    IMPACT: Reproducible experiments, easier collaboration

USAGE:
    python scripts/train.py --model resnet50 --epochs 50 --batch-size 32
    
FEATURES:
    - Multiple model architectures (ResNet50, VGG16, EfficientNet)
    - Configurable hyperparameters
    - Automatic checkpointing
    - TensorBoard logging
    - Early stopping
    - Learning rate scheduling

COMMAND-LINE ARGUMENTS:
    --model: Model architecture (resnet50, vgg16, efficientnet_b0/b1/b2)
    --epochs: Number of training epochs (default: 50)
    --batch-size: Batch size (default: 32)
    --learning-rate: Initial learning rate (default: 0.001)
    --data-dir: Data directory (default: data/processed)
    --save-dir: Model save directory (default: models)
    --config: Config file path (optional, overrides defaults)

EXAMPLE USE:
    # Train ResNet50 for 50 epochs
    python scripts/train.py --model resnet50 --epochs 50
    
    # Train EfficientNet-B0 with custom batch size
    python scripts/train.py --model efficientnet_b0 --batch-size 64
    
    # Use custom config file
    python scripts/train.py --config configs/my_config.yaml
"""

import argparse
import yaml
import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.dataset import FractureDataset
from src.models.model_factory import ModelFactory
from src.training.trainer import Trainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Train fracture detection model')
    
    parser.add_argument(
        '--config',
        type=str,
        default='configs/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='resnet50',
        choices=['vgg16', 'resnet50', 'efficientnet_b0', 'efficientnet_b1'],
        help='Model architecture'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=50,
        help='Number of training epochs'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/processed',
        help='Path to processed data directory'
    )
    
    parser.add_argument(
        '--save-dir',
        type=str,
        default='models/checkpoints',
        help='Directory to save model checkpoints'
    )
    
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def main():
    """Main training function"""
    args = parse_args()
    
    logger.info("=" * 60)
    logger.info("Fracture Detection AI - Training")
    logger.info("=" * 60)
    
    # Load configuration
    logger.info(f"Loading configuration from {args.config}")
    config = load_config(args.config)
    
    # Override config with command line arguments
    config['model']['architecture'] = args.model
    config['training']['epochs'] = args.epochs
    config['data']['batch_size'] = args.batch_size
    
    # Create datasets
    logger.info("Loading datasets...")
    train_dataset = FractureDataset(
        data_dir=args.data_dir,
        split='train',
        image_size=(config['data']['image_size'], config['data']['image_size']),
        batch_size=config['data']['batch_size']
    )
    
    val_dataset = FractureDataset(
        data_dir=args.data_dir,
        split='validation',
        image_size=(config['data']['image_size'], config['data']['image_size']),
        batch_size=config['data']['batch_size']
    )
    
    # Create TensorFlow datasets
    train_data = train_dataset.create_tf_dataset()
    val_data = val_dataset.create_tf_dataset()
    
    logger.info(f"Training samples: {len(train_dataset)}")
    logger.info(f"Validation samples: {len(val_dataset)}")
    
    # Create model
    logger.info(f"Creating {args.model} model...")
    model_wrapper = ModelFactory.create_model(
        model_name=args.model,
        input_shape=(config['data']['image_size'], config['data']['image_size'], 3),
        num_classes=config['data']['num_classes'],
        freeze_base=config['model']['freeze_layers'] > 0,
        dropout_rate=config['model']['dropout_rate']
    )
    
    model_wrapper.build_model()
    model_wrapper.compile_model(
        optimizer=config['training']['optimizer'],
        learning_rate=config['training']['learning_rate'],
        loss=config['training']['loss']
    )
    
    model_wrapper.summary()
    
    # Create trainer
    logger.info("Initializing trainer...")
    trainer = Trainer(
        model=model_wrapper.model,
        config=config['training'],
        save_dir=args.save_dir
    )
    
    # Train model
    logger.info(f"Starting training for {args.epochs} epochs...")
    history = trainer.train(
        train_data=train_data,
        val_data=val_data,
        epochs=args.epochs
    )
    
    # Save final model
    final_model_path = os.path.join('models/final', f'{args.model}_final.h5')
    os.makedirs('models/final', exist_ok=True)
    trainer.save_final_model(final_model_path)
    
    # Print training summary
    summary = trainer.get_training_summary()
    logger.info("\n" + "=" * 60)
    logger.info("Training Summary")
    logger.info("=" * 60)
    for key, value in summary.items():
        logger.info(f"{key}: {value}")
    
    logger.info("\nTraining completed successfully!")


if __name__ == "__main__":
    main()
