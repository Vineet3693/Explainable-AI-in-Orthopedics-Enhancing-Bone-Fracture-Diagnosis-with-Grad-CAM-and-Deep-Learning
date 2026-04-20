"""
Training package for model training orchestration

PACKAGE PURPOSE:
    Contains modules for training fracture detection models including
    training orchestration, custom callbacks, and medical AI monitoring.

MODULES:
    - trainer.py: Main training orchestrator
    - callbacks.py: Custom Keras callbacks for medical AI

KEY CONCEPTS:
    - Callbacks: Functions called during training (checkpointing, logging)
    - Early Stopping: Stop training when validation loss plateaus
    - Model Checkpointing: Save best model during training
    - Learning Rate Scheduling: Adjust learning rate dynamically
    - TensorBoard: Visualization of training metrics
    - False Negative Monitoring: Track missed fractures (patient safety)

CUSTOM CALLBACKS:
    - MetricsLogger: Log detailed metrics to file
    - GradCAMCallback: Generate Grad-CAM visualizations during training
    - FalseNegativeMonitor: Alert if FN rate > 5%
    - LearningRateScheduler: Adaptive learning rate

USAGE:
    from src.training import Trainer
    
    trainer = Trainer(model, config)
    history = trainer.train(train_data, val_data)
"""

__all__ = [
    'Trainer',
    'MetricsLoggerCallback',
    'GradCAMCallback',
    'FalseNegativeMonitor'
]
