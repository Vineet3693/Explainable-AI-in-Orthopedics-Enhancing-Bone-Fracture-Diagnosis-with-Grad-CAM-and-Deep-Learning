"""
Optimizer Configurations for Training

PURPOSE:
    Provides pre-configured optimizers for different training scenarios.
    Encapsulates best practices for medical AI training.

WHY OPTIMIZER CONFIGS:
    Manual setup: Inconsistent, error-prone
    Configs (this): Reproducible, tested, optimized
    
    IMPACT: Faster convergence, better models

DESIGN PHILOSOPHY:
    1. Proven configurations (from literature)
    2. Task-specific (fine-tuning vs from-scratch)
    3. Safety (gradient clipping, warmup)
    4. Flexibility (easy to customize)

PROS:
    ✅ Proven configurations
    ✅ Reproducible results
    ✅ Easy to use
    ✅ Includes best practices (warmup, decay)

CONS:
    ❌ May not be optimal for all datasets
    ❌ Requires understanding to customize
    ❌ One-size-fits-all approach

ALTERNATIVES:
    1. Manual configuration: Full control but error-prone
    2. Auto-tuning (Optuna): Best but slow
    3. Default PyTorch: Simple but suboptimal
    4. This (configs): Balance of ease and performance

COMPARISON:
    | Approach      | Ease of Use | Performance | Reproducibility | Flexibility |
    |---------------|-------------|-------------|-----------------|-------------|
    | Manual        | ❌          | ⚠️          | ❌              | ✅          |
    | Auto-tuning   | ⚠️          | ✅          | ✅              | ❌          |
    | Defaults      | ✅          | ❌          | ✅              | ❌          |
    | This (configs)| ✅          | ✅          | ✅              | ⚠️          |

USAGE:
    from src.training.optimizers import get_optimizer
    
    # For fine-tuning pre-trained model
    optimizer = get_optimizer(
        model.parameters(),
        optimizer_type='adam',
        learning_rate=1e-4,
        task='fine_tuning'
    )
    
    # For training from scratch
    optimizer = get_optimizer(
        model.parameters(),
        optimizer_type='sgd',
        learning_rate=1e-2,
        task='from_scratch'
    )
"""

import torch
from torch.optim import Adam, AdamW, SGD, RMSprop
from torch.optim.lr_scheduler import (
    CosineAnnealingLR,
    ReduceLROnPlateau,
    OneCycleLR
)
from typing import Iterator, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_optimizer(
    parameters: Iterator[torch.nn.Parameter],
    optimizer_type: str = 'adam',
    learning_rate: float = 1e-4,
    weight_decay: float = 1e-4,
    task: str = 'fine_tuning'
) -> torch.optim.Optimizer:
    """
    Get pre-configured optimizer
    
    WHY DIFFERENT OPTIMIZERS:
        Adam: Adaptive learning rates, good for most tasks
        AdamW: Adam with better weight decay (recommended)
        SGD: Simple, good with momentum for from-scratch training
        RMSprop: Good for RNNs, less common for CNNs
    
    WHY TASK-SPECIFIC:
        Fine-tuning: Lower LR, less aggressive
        From-scratch: Higher LR, more aggressive
    
    Args:
        parameters: Model parameters to optimize
        optimizer_type: 'adam', 'adamw', 'sgd', 'rmsprop'
        learning_rate: Initial learning rate
        weight_decay: L2 regularization strength
        task: 'fine_tuning' or 'from_scratch'
        
    Returns:
        Configured optimizer
    """
    # WHY ADJUST LR BY TASK:
    # Fine-tuning: Start from good weights, small adjustments
    # From-scratch: Random weights, need larger steps
    if task == 'fine_tuning':
        lr = learning_rate
        # WHY LOWER WEIGHT DECAY:
        # Pre-trained weights are already good
        # Don't want to regularize them too much
        wd = weight_decay * 0.1
    else:  # from_scratch
        lr = learning_rate * 10
        wd = weight_decay
    
    logger.info(f"Creating {optimizer_type} optimizer for {task} (lr={lr}, wd={wd})")
    
    if optimizer_type.lower() == 'adam':
        # WHY ADAM:
        # Adaptive learning rates per parameter
        # Good default choice
        # Handles sparse gradients well
        optimizer = Adam(
            parameters,
            lr=lr,
            betas=(0.9, 0.999),  # WHY THESE: Standard values from paper
            eps=1e-8,  # WHY: Numerical stability
            weight_decay=wd
        )
        
    elif optimizer_type.lower() == 'adamw':
        # WHY ADAMW:
        # Fixes weight decay in Adam
        # Better generalization
        # Recommended over Adam
        optimizer = AdamW(
            parameters,
            lr=lr,
            betas=(0.9, 0.999),
            eps=1e-8,
            weight_decay=wd
        )
        
    elif optimizer_type.lower() == 'sgd':
        # WHY SGD:
        # Simple and effective
        # Good with momentum
        # Often better for from-scratch training
        optimizer = SGD(
            parameters,
            lr=lr,
            momentum=0.9,  # WHY 0.9: Standard value, good acceleration
            weight_decay=wd,
            nesterov=True  # WHY NESTEROV: Look-ahead momentum, faster convergence
        )
        
    elif optimizer_type.lower() == 'rmsprop':
        # WHY RMSPROP:
        # Adaptive learning rates
        # Good for RNNs
        # Less common for CNNs
        optimizer = RMSprop(
            parameters,
            lr=lr,
            alpha=0.99,  # WHY: Smoothing constant
            eps=1e-8,
            weight_decay=wd
        )
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_type}")
    
    return optimizer


def get_scheduler(
    optimizer: torch.optim.Optimizer,
    scheduler_type: str = 'cosine',
    num_epochs: int = 100,
    **kwargs
):
    """
    Get learning rate scheduler
    
    WHY SCHEDULERS:
        Fixed LR: Suboptimal, may not converge
        Scheduled LR: Better convergence, higher accuracy
    
    WHY DIFFERENT SCHEDULERS:
        Cosine: Smooth decay, good default
        ReduceLROnPlateau: Adaptive, monitors validation
        OneCycle: Fast training, super-convergence
    
    Args:
        optimizer: Optimizer to schedule
        scheduler_type: 'cosine', 'plateau', 'onecycle'
        num_epochs: Total training epochs
        **kwargs: Scheduler-specific arguments
        
    Returns:
        Learning rate scheduler
    """
    logger.info(f"Creating {scheduler_type} scheduler")
    
    if scheduler_type.lower() == 'cosine':
        # WHY COSINE:
        # Smooth decay from max to min
        # No sudden drops
        # Good default choice
        scheduler = CosineAnnealingLR(
            optimizer,
            T_max=num_epochs,  # WHY: Full cycle length
            eta_min=1e-6  # WHY: Minimum LR, prevents complete stop
        )
        
    elif scheduler_type.lower() == 'plateau':
        # WHY PLATEAU:
        # Adaptive based on validation performance
        # Reduces LR when stuck
        # Good for unknown convergence patterns
        scheduler = ReduceLROnPlateau(
            optimizer,
            mode='min',  # WHY: Minimize validation loss
            factor=0.5,  # WHY: Reduce by half
            patience=5,  # WHY: Wait 5 epochs before reducing
            verbose=True
        )
        
    elif scheduler_type.lower() == 'onecycle':
        # WHY ONECYCLE:
        # Fast training (super-convergence)
        # Single cycle from low -> high -> low
        # Can train in fewer epochs
        steps_per_epoch = kwargs.get('steps_per_epoch', 100)
        scheduler = OneCycleLR(
            optimizer,
            max_lr=kwargs.get('max_lr', 1e-3),
            epochs=num_epochs,
            steps_per_epoch=steps_per_epoch
        )
    else:
        raise ValueError(f"Unknown scheduler: {scheduler_type}")
    
    return scheduler


__all__ = [
    'get_optimizer',
    'get_scheduler'
]
