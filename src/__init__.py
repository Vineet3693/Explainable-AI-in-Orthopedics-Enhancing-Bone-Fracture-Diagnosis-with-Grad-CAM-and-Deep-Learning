"""
Root Package Initialization for Fracture Detection AI

PURPOSE:
    Main package initialization that sets up the entire project.
    Provides version info and top-level imports.

PACKAGE STRUCTURE:
    src/
        data/           - Data pipeline
        models/         - CNN architectures
        validators/     - Input validation
        training/       - Training orchestration
        evaluation/     - Model evaluation
        explainability/ - Grad-CAM, interpretability
        llm_integration/- Gemini, Groq clients
        prompts/        - LLM prompt templates
        monitoring/     - Metrics, logging, alerts
        qa_system/      - Question answering
        agents/         - LangGraph workflows
        workflows/      - Task sequences
        utils/          - Helper functions

VERSION HISTORY:
    1.0.0 - Initial release with core functionality
    1.1.0 - Added validation pipeline
    1.2.0 - Added LLM integration
    1.3.0 - Added monitoring system
    1.4.0 - Added Q&A system
"""

__version__ = '1.4.0'
__author__ = 'Fracture Detection AI Team'
__license__ = 'MIT'

# Top-level imports for convenience
from src.data import FractureDataset, ImagePreprocessor
from src.models import ModelFactory
from src.validators import ImageValidator
from src.training import Trainer
from src.evaluation import Evaluator
from src.explainability import GradCAM
from src.llm_integration import GeminiClient, GroqClient
from src.qa_system import QuestionClassifier, AnswerGenerator

__all__ = [
    '__version__',
    'FractureDataset',
    'ImagePreprocessor',
    'ModelFactory',
    'ImageValidator',
    'Trainer',
    'Evaluator',
    'GradCAM',
    'GeminiClient',
    'GroqClient',
    'QuestionClassifier',
    'AnswerGenerator'
]
