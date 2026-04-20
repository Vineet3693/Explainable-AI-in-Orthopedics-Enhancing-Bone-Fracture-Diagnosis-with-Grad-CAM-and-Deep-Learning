"""
Prompts package for LLM prompt templates

PACKAGE PURPOSE:
    Contains structured prompt templates for Gemini and Groq LLMs.
    Ensures consistent, high-quality outputs through well-engineered prompts.

SUBPACKAGES:
    - gemini/: Prompt templates for Gemini (vision + text)
    - groq/: Prompt templates for Groq (text-only)

KEY CONCEPTS:
    - Prompt Engineering: Crafting effective instructions for LLMs
    - System Prompt: Instructions defining AI behavior and constraints
    - User Prompt: Specific task or question from user
    - Few-shot Learning: Providing examples in prompts
    - Chain-of-Thought: Asking LLM to explain reasoning
    - Temperature: Controls randomness (0=deterministic, 1=creative)

PROMPT BEST PRACTICES:
    1. Be specific and clear
    2. Provide context and examples
    3. Define output format (JSON, markdown, etc.)
    4. Include safety guidelines
    5. Add medical disclaimers
    6. Use structured templates

USAGE:
    from src.prompts.gemini import RADIOLOGY_REPORT_PROMPT
    from src.prompts.groq import PATIENT_SUMMARY_PROMPT
    
    prompt = RADIOLOGY_REPORT_PROMPT.format(
        prediction='fracture',
        confidence=0.95,
        anatomy='wrist'
    )
"""

__all__ = [
    'RADIOLOGY_REPORT_PROMPT',
    'PATIENT_SUMMARY_PROMPT',
    'QA_PROMPT',
    'TRANSLATION_PROMPT'
]
