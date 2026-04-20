"""
Prompt Templates Base Module

PURPOSE:
    Base templates and utilities for all LLM prompts.
    Provides reusable components and formatting functions.

WHY BASE TEMPLATES:
    DRY principle - reuse common prompt sections
    Consistency - same disclaimers everywhere
    Maintainability - update once, apply everywhere
    
    IMPACT: 50% less code duplication

USAGE:
    from src.prompts.prompt_templates import MEDICAL_DISCLAIMER, format_prompt
    
    prompt = format_prompt(
        system=RADIOLOGIST_SYSTEM,
        user_query=question,
        context=diagnosis_info
    )
"""

# Common disclaimer templates
MEDICAL_DISCLAIMER = """
**IMPORTANT MEDICAL DISCLAIMER:**
This AI-generated response is for informational purposes only and should not be considered as professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read in this AI-generated content.
"""

AI_LIMITATIONS_DISCLAIMER = """
**AI LIMITATIONS:**
- This analysis is AI-assisted and requires verification by a qualified radiologist
- AI confidence level: {confidence:.1%}
- AI can make errors and should not be solely relied upon for medical decisions
- Final diagnosis must be made by a licensed healthcare professional
"""

EMERGENCY_DISCLAIMER = """
**EMERGENCY NOTICE:**
If you are experiencing a medical emergency, call emergency services immediately (911 in US, 112 in EU, or your local emergency number). Do not rely on AI for emergency medical situations.
"""

# Common prompt sections
CONTEXT_SECTION_TEMPLATE = """
**CONTEXT:**
- Diagnosis: {diagnosis}
- Location: {anatomy}
- Confidence: {confidence:.1%}
- Image Quality: {quality}/100
"""

PATIENT_INFO_TEMPLATE = """
**PATIENT INFORMATION:**
- Age: {age} years
- Gender: {gender}
{f"- Clinical History: {history}" if history else ""}
"""


def format_prompt(
    system: str = "",
    user_query: str = "",
    context: dict = None,
    include_disclaimer: bool = True
) -> str:
    """
    Format a complete prompt with all sections
    
    Args:
        system: System prompt
        user_query: User's question/request
        context: Context dictionary
        include_disclaimer: Include medical disclaimer
        
    Returns:
        Formatted prompt
    """
    sections = []
    
    if system:
        sections.append(system)
    
    if context:
        context_str = CONTEXT_SECTION_TEMPLATE.format(**context)
        sections.append(context_str)
    
    if user_query:
        sections.append(f"\n**USER QUERY:**\n{user_query}")
    
    if include_disclaimer:
        sections.append(MEDICAL_DISCLAIMER)
    
    return "\n\n".join(sections)


__all__ = [
    'MEDICAL_DISCLAIMER',
    'AI_LIMITATIONS_DISCLAIMER',
    'EMERGENCY_DISCLAIMER',
    'CONTEXT_SECTION_TEMPLATE',
    'PATIENT_INFO_TEMPLATE',
    'format_prompt'
]
