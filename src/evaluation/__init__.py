"""
Evaluation package for model performance assessment

PACKAGE PURPOSE:
    Contains modules for comprehensive model evaluation with medical AI
    specific metrics. Focuses on patient safety metrics like sensitivity
    and false negative rate.

MODULES:
    - evaluator.py: Comprehensive model evaluation

KEY CONCEPTS:
    - Sensitivity/Recall: % of fractures correctly detected (>95% target)
    - Specificity: % of normal X-rays correctly identified (>85% target)
    - False Negative Rate: % of fractures missed (<5% target)
    - Precision: % of fracture predictions that are correct (>90% target)
    - F1-Score: Harmonic mean of precision and recall (>92% target)
    - AUC-ROC: Area under ROC curve (>0.95 target)
    - Confusion Matrix: 2x2 matrix showing TP, TN, FP, FN

MEDICAL AI METRIC PRIORITY:
    1. Recall/Sensitivity (Most Important) - Don't miss fractures
    2. False Negative Rate - Direct patient safety metric
    3. Specificity - Avoid too many false alarms
    4. Precision - Reduce unnecessary worry
    5. F1-Score - Balance precision and recall
    6. AUC-ROC - Overall performance
    7. Accuracy (Least Important) - Can be misleading

USAGE:
    from src.evaluation import Evaluator
    
    evaluator = Evaluator(model)
    metrics = evaluator.evaluate(test_data)
    print(f"Recall: {metrics['recall']:.2%}")
"""

__all__ = [
    'Evaluator',
    'calculate_metrics',
    'plot_confusion_matrix',
    'plot_roc_curve'
]
