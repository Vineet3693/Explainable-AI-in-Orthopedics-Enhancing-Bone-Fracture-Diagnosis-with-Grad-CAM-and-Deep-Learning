"""
Groq Translation Prompts for Multi-language Support

PURPOSE:
    Fast, accurate translation of medical content using Groq.
    Supports multiple languages for global accessibility.

WHY GROQ FOR TRANSLATION:
    Gemini: Better quality but slower
    Groq: 5x faster, good enough for medical summaries
    
    IMPACT: Real-time translation, better patient access

DESIGN PHILOSOPHY:
    1. Medical accuracy (preserve meaning)
    2. Cultural appropriateness
    3. Simple language (accessible)
    4. Fast (< 1 second)

SUPPORTED LANGUAGES:
    - English (default)
    - Hindi (हिंदी)
    - Spanish (Español)
    - French (Français)
    - Arabic (العربية)
    - Chinese (中文)

USAGE:
    from src.prompts.groq.translation_prompts import generate_translation_prompt
    
    prompt = generate_translation_prompt(
        text='You have a wrist fracture',
        target_language='hindi'
    )
"""

def generate_translation_prompt(
    text: str,
    target_language: str,
    content_type: str = 'medical_summary'
) -> str:
    """
    Generate translation prompt
    
    WHY SPECIFY CONTENT TYPE:
        Medical text needs special handling
        Different formality levels
        Preserve medical accuracy
    
    Args:
        text: Text to translate
        target_language: Target language
        content_type: Type of content
        
    Returns:
        Translation prompt
    """
    
    language_names = {
        'hindi': 'Hindi (हिंदी)',
        'spanish': 'Spanish (Español)',
        'french': 'French (Français)',
        'arabic': 'Arabic (العربية)',
        'chinese': 'Chinese (中文)',
        'portuguese': 'Portuguese (Português)',
        'german': 'German (Deutsch)',
        'japanese': 'Japanese (日本語)'
    }
    
    lang_name = language_names.get(target_language.lower(), target_language)
    
    prompt = f"""
Translate the following medical text to {lang_name}:

**TEXT TO TRANSLATE:**
{text}

**INSTRUCTIONS:**
1. Maintain medical accuracy
2. Use appropriate medical terminology in {lang_name}
3. Keep the same tone and formality
4. Preserve all important information
5. Use culturally appropriate language

**IMPORTANT:**
- Medical terms: Use standard medical terms in {lang_name} or keep English term with explanation
- Numbers and measurements: Keep as is
- Proper nouns: Keep in original language
- Ensure translation is clear and understandable

**OUTPUT:**
Provide only the translated text, no explanations.
"""
    
    return prompt


def generate_bilingual_prompt(
    text: str,
    target_language: str
) -> str:
    """
    Generate bilingual output (English + target language)
    
    WHY BILINGUAL:
        Patients may understand both languages
        Helps verify translation accuracy
        Useful for family members
    
    Args:
        text: Text to translate
        target_language: Target language
        
    Returns:
        Bilingual prompt
    """
    
    prompt = f"""
Provide bilingual output (English and {target_language}):

**ENGLISH:**
{text}

**INSTRUCTIONS:**
1. Translate to {target_language}
2. Format as:
   - English version first
   - {target_language} version below
   - Clear separation between versions

**OUTPUT FORMAT:**
**English:**
[English text]

**{target_language.title()}:**
[Translated text]
"""
    
    return prompt


def generate_simple_translation_prompt(
    text: str,
    target_language: str
) -> str:
    """
    Ultra-fast simple translation
    
    WHY SIMPLE:
        For short phrases, don't need complex instructions
        Faster response
        Lower token usage
    
    Args:
        text: Short text to translate
        target_language: Target language
        
    Returns:
        Simple translation prompt
    """
    
    prompt = f"""
Translate to {target_language}:

{text}

Keep medical accuracy. Output translation only.
"""
    
    return prompt


__all__ = [
    'generate_translation_prompt',
    'generate_bilingual_prompt',
    'generate_simple_translation_prompt'
]
