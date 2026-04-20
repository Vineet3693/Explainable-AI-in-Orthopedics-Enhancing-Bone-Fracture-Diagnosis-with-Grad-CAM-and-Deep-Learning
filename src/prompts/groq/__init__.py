"""
Groq prompt templates for fast text generation

PURPOSE:
    Structured prompt templates for Groq API calls.
    Optimized for fast, text-only medical responses.

PROMPTS:
    - PATIENT_SUMMARY_PROMPT: Simplify medical reports
    - QUICK_QA_PROMPT: Fast question answering
    - TRANSLATION_PROMPT: Multi-language translation
    - FOLLOW_UP_PROMPT: Conversational follow-ups

KEY FEATURES:
    - Concise, focused prompts
    - Fast response optimization
    - Patient-friendly language
    - Safety disclaimers
"""

# Patient Summary Prompt
PATIENT_SUMMARY_PROMPT = """Convert the following medical report into a simple, patient-friendly summary:

**MEDICAL REPORT:**
{medical_report}

**INSTRUCTIONS:**
1. Use simple, everyday language (avoid medical jargon)
2. Explain key findings clearly
3. Highlight important points
4. Keep it concise (2-3 paragraphs)
5. Be reassuring but honest
6. Include next steps

**OUTPUT:** Plain text summary suitable for patients

Generate summary:
"""

# Quick Q&A Prompt
QUICK_QA_PROMPT = """Answer this medical question briefly and clearly:

**QUESTION:** {question}

**CONTEXT:** {context}

**INSTRUCTIONS:**
1. Provide a clear, concise answer (2-3 sentences)
2. Use simple language
3. Be accurate and evidence-based
4. Add disclaimer if needed

Answer:
"""

# Translation Prompt
TRANSLATION_PROMPT = """Translate the following medical text to {target_language}:

**TEXT TO TRANSLATE:**
{text}

**INSTRUCTIONS:**
1. Maintain medical accuracy
2. Use appropriate medical terminology in target language
3. Preserve formatting
4. Keep the same tone and style

**IMPORTANT:** Ensure translation is medically accurate and culturally appropriate.

Translation:
"""

# Follow-up Question Prompt
FOLLOW_UP_PROMPT = """Based on the conversation history, answer this follow-up question:

**CONVERSATION HISTORY:**
{conversation_history}

**FOLLOW-UP QUESTION:**
{question}

**INSTRUCTIONS:**
1. Consider previous context
2. Provide relevant, consistent answer
3. Be concise and clear
4. Maintain conversational tone

Answer:
"""

# Treatment Information Prompt
TREATMENT_INFO_PROMPT = """Provide general information about treatment for {condition}:

**INSTRUCTIONS:**
1. Describe common treatment approaches
2. Explain typical recovery timeline
3. Mention general do's and don'ts
4. Use simple, understandable language
5. Emphasize consulting with doctor

**DISCLAIMER:** This is general information only. Specific treatment should be determined by a healthcare provider.

Treatment information:
"""

__all__ = [
    'PATIENT_SUMMARY_PROMPT',
    'QUICK_QA_PROMPT',
    'TRANSLATION_PROMPT',
    'FOLLOW_UP_PROMPT',
    'TREATMENT_INFO_PROMPT'
]
