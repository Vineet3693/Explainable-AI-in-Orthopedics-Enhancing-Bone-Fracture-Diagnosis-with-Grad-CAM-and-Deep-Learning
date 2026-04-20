"""
Groq Summary Prompts for Fast Patient Summaries

PURPOSE:
    Generates concise, patient-friendly summaries of medical reports using
    Groq's fast text generation. Optimized for speed and clarity.

WHY GROQ FOR SUMMARIES:
    Gemini: Slower but multimodal
    Groq: 10x faster for text-only tasks
    
    IMPACT: Sub-second response times, better UX

DESIGN PHILOSOPHY:
    1. Speed first (use Groq's fast inference)
    2. Simple language (patient-friendly)
    3. Concise (2-3 paragraphs max)
    4. Actionable (clear next steps)

KEY CONCEPTS:
    - Patient Summary: Simplified medical report
    - Plain Language: No medical jargon
    - Actionable: Clear next steps
    - Empathetic: Reassuring tone

PROS:
    ✅ Very fast (< 1 second)
    ✅ Low cost ($0.0001/1k tokens)
    ✅ Patient-friendly language
    ✅ Consistent format

CONS:
    ❌ Text-only (can't analyze images)
    ❌ Less sophisticated than Gemini
    ❌ May oversimplify complex cases

ALTERNATIVES:
    1. Gemini: Better quality but slower
    2. Groq (this): Fast and cheap
    3. Pre-defined templates: Fastest but rigid
    4. Human summary: Best but expensive

COMPARISON:
    Approach    | Speed      | Cost    | Quality | Flexibility
    Gemini      | 2-3s       | Medium  | High    | High
    Groq        | <1s        | Low     | Good    | High
    Templates   | Instant    | Free    | Medium  | Low
    Human       | Minutes    | High    | Highest | Highest

USAGE:
    from src.prompts.groq.summary_prompts import generate_patient_summary_prompt
    
    prompt = generate_patient_summary_prompt(
        report='[Full radiology report]',
        language='english'
    )
"""

def generate_patient_summary_prompt(
    report: str,
    language: str = 'english',
    reading_level: str = 'general'
) -> str:
    """
    Generate prompt for patient-friendly summary
    
    WHY DIFFERENT READING LEVELS:
        General public: 8th grade reading level
        Medical professionals: Can use more terminology
        Children/elderly: Even simpler language
    
    Args:
        report: Full radiology report
        language: Target language (english, hindi, spanish)
        reading_level: Target reading level
        
    Returns:
        Summary generation prompt
    """
    
    # WHY SPECIFY READING LEVEL:
    # Medical literacy varies widely
    # Need to match patient's comprehension
    # Too complex: Patient confused
    # Too simple: Patient feels patronized
    
    reading_level_guidance = {
        'general': 'Use simple, everyday language suitable for 8th grade reading level',
        'medical': 'You may use basic medical terms but explain them',
        'simple': 'Use very simple language suitable for children or non-native speakers'
    }
    
    prompt = f"""
Convert the following medical report into a patient-friendly summary in {language}:

**MEDICAL REPORT:**
{report}

**INSTRUCTIONS:**
Create a brief, clear summary (2-3 paragraphs) that:

1. **EXPLAINS THE FINDINGS**
   - What the X-ray shows in simple terms
   - Avoid medical jargon
   - Use everyday language
   - {reading_level_guidance.get(reading_level, '')}

2. **WHAT IT MEANS**
   - Is this serious or minor?
   - What happens next?
   - How long will recovery take (if applicable)?

3. **NEXT STEPS**
   - What should the patient do?
   - When to see a doctor?
   - Any immediate actions needed?

**TONE:**
- Warm and reassuring
- Clear and direct
- Empathetic but honest
- Not alarming

**IMPORTANT:**
- Keep it under 200 words
- Use bullet points for clarity
- Include a disclaimer that they should discuss with their doctor
- Avoid scary medical terminology

**OUTPUT FORMAT:**
Plain text summary suitable for patients to read and understand.
"""
    
    return prompt


def generate_quick_summary_prompt(
    diagnosis: str,
    confidence: float,
    anatomy: str
) -> str:
    """
    Generate ultra-fast summary (emergency/urgent cases)
    
    WHY ULTRA-FAST:
        Emergency situations need immediate info
        Groq can respond in <500ms
        Critical for urgent cases
    
    Args:
        diagnosis: Diagnosis result
        confidence: Confidence level
        anatomy: Affected area
        
    Returns:
        Quick summary prompt
    """
    
    prompt = f"""
Generate a 2-sentence summary for:
- Finding: {diagnosis}
- Location: {anatomy}
- Confidence: {confidence:.0%}

Be clear, direct, and include urgency level (urgent/routine).
"""
    
    return prompt


def generate_family_explanation_prompt(
    summary: str,
    patient_age: int,
    relationship: str = 'family_member'
) -> str:
    """
    Generate explanation for family members
    
    WHY FAMILY-SPECIFIC:
        Family members need different info than patients
        May need to help with care
        Different concerns and questions
    
    Args:
        summary: Patient summary
        patient_age: Patient's age
        relationship: Relationship to patient
        
    Returns:
        Family explanation prompt
    """
    
    prompt = f"""
Explain the following medical summary to a {relationship} of a {patient_age}-year-old patient:

**SUMMARY:**
{summary}

**INSTRUCTIONS:**
Create an explanation that:

1. **EXPLAINS THE SITUATION**
   - What happened
   - What the X-ray shows
   - How serious it is

2. **CARE INSTRUCTIONS**
   - How to help the patient
   - What to watch for
   - When to seek help

3. **RECOVERY EXPECTATIONS**
   - Timeline
   - What's normal during healing
   - When to worry

**TONE:**
- Supportive and informative
- Practical and actionable
- Reassuring but realistic

Keep it concise (under 150 words) and focused on practical care.
"""
    
    return prompt


def generate_multilingual_summary_prompt(
    report: str,
    target_language: str,
    include_original: bool = True
) -> str:
    """
    Generate summary in multiple languages
    
    WHY MULTILINGUAL:
        Patients speak different languages
        Medical information must be accessible
        Better patient understanding = better outcomes
    
    Args:
        report: Medical report
        target_language: Target language
        include_original: Include English version
        
    Returns:
        Multilingual summary prompt
    """
    
    prompt = f"""
Translate and summarize this medical report into {target_language}:

**REPORT:**
{report}

**INSTRUCTIONS:**
1. Translate key findings accurately
2. Maintain medical accuracy
3. Use culturally appropriate language
4. Keep medical terms if no good translation exists (explain them)
5. Ensure clarity and readability

{f"Include both {target_language} and English versions." if include_original else ""}

**IMPORTANT:**
- Medical accuracy is critical
- Use appropriate formality level for {target_language}
- Include disclaimer in {target_language}
"""
    
    return prompt


__all__ = [
    'generate_patient_summary_prompt',
    'generate_quick_summary_prompt',
    'generate_family_explanation_prompt',
    'generate_multilingual_summary_prompt'
]
