"""
LLM Integration package for AI-powered text generation

PACKAGE PURPOSE:
    Contains clients for integrating Large Language Models (Gemini and Groq)
    for generating radiology reports, patient summaries, and answering
    medical questions.

MODULES:
    - gemini_client.py: Google Gemini API client (vision + text)
    - groq_client.py: Groq API client (fast text generation)

DUAL LLM STRATEGY:
    GEMINI (Vision + Complex):
        - Radiology report generation (needs vision)
        - X-ray image analysis (needs vision)
        - Complex medical reasoning
        - Cost: $0.002 per image, $0.0005 per 1k tokens
        - Speed: 2-3 seconds
    
    GROQ (Text + Speed):
        - Patient summaries (text-only, fast)
        - Simple Q&A (text-only, fast)
        - Translations (text-only, fast)
        - Cost: $0.0001 per 1k tokens
        - Speed: 0.5-1 second
    
    SAVINGS: 50% cost reduction by using right tool for each task

KEY CONCEPTS:
    - LLM: Large Language Model (AI trained on massive text data)
    - Multimodal: Can process both images and text (Gemini)
    - Token: Unit of text (roughly 4 characters or 0.75 words)
    - Prompt Engineering: Crafting effective instructions for LLMs
    - Temperature: Controls randomness (0=deterministic, 1=creative)
    - Context Window: Maximum input length LLM can process

COST OPTIMIZATION:
    Task Type           | Provider | Cost/Request | Savings
    Radiology report    | Gemini   | $0.002       | N/A
    Patient summary     | Groq     | $0.0001      | 80%
    Simple Q&A          | Groq     | $0.0001      | 80%
    Translation         | Groq     | $0.0001      | 80%

USAGE:
    from src.llm_integration import GeminiClient, GroqClient
    
    gemini = GeminiClient(api_key='...')
    report = gemini.generate_radiology_report(xray_image, prediction)
    
    groq = GroqClient(api_key='...')
    summary = groq.generate_patient_summary(report)
"""

__all__ = [
    'GeminiClient',
    'GroqClient'
]
