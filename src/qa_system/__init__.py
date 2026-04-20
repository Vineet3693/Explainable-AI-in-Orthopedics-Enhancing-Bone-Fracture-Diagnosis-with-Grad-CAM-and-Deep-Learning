"""
Q&A System package for patient question answering

PACKAGE PURPOSE:
    Contains modules for classifying patient questions and generating
    appropriate answers using pre-defined responses or LLMs. Optimizes
    cost and response time by routing questions intelligently.

MODULES:
    - question_classifier.py: Classify questions into categories
    - answer_generator.py: Generate answers using appropriate strategy

QUESTION CATEGORIES:
    1. FACTUAL (30% of questions)
       - "What is a fracture?"
       - "How long does healing take?"
       - Handler: Pre-defined answers (instant, free)
    
    2. DIAGNOSIS-SPECIFIC (40% of questions)
       - "What does my diagnosis mean?"
       - "Is this serious?"
       - Handler: Gemini (context-aware, $0.0005)
    
    3. TREATMENT (20% of questions)
       - "What treatment do I need?"
       - "Can I exercise?"
       - Handler: Groq (fast, $0.0001)
    
    4. SPECIALIST (10% of questions)
       - Complex medical questions
       - Handler: Refer to doctor

KEY CONCEPTS:
    - Question Classification: Categorizing questions for routing
    - Answer Strategy: Different approaches for different question types
    - Pre-defined Answers: Fast, consistent, free responses
    - LLM-based Answers: Contextual, flexible, but costs money
    - Medical Disclaimers: All answers include safety warnings

COST OPTIMIZATION:
    Without classification: All questions to LLM = $0.0005 average
    With classification: 30% free, 70% LLM = $0.0003 average
    SAVINGS: 40% cost reduction

USAGE:
    from src.qa_system import QuestionClassifier, AnswerGenerator
    
    classifier = QuestionClassifier()
    category = classifier.classify("What is a fracture?")
    
    generator = AnswerGenerator()
    answer = generator.generate(question, category, context)
"""

__all__ = [
    'QuestionClassifier',
    'AnswerGenerator'
]
