"""
Gemini Q&A Prompts for Medical Questions

PURPOSE:
    Comprehensive Q&A prompts for answering patient questions about
    fractures, treatment, and recovery using Gemini's advanced reasoning.

WHY GEMINI FOR COMPLEX Q&A:
    Simple questions: Knowledge base (free, instant)
    Complex questions: Gemini (better reasoning, context-aware)
    
    IMPACT: Better answers for complex medical questions

DESIGN PHILOSOPHY:
    1. Context-aware (use diagnosis info)
    2. Evidence-based (cite medical knowledge)
    3. Patient-centered (empathetic tone)
    4. Safe (appropriate disclaimers)

USAGE:
    from src.prompts.gemini.qa_prompts import generate_medical_qa_prompt
    
    prompt = generate_medical_qa_prompt(
        question='Will I need surgery?',
        diagnosis_context={'prediction': 'fracture', 'anatomy': 'wrist'}
    )
"""

def generate_medical_qa_prompt(
    question: str,
    diagnosis_context: dict,
    conversation_history: list = None
) -> str:
    """
    Generate prompt for medical Q&A
    
    WHY INCLUDE DIAGNOSIS CONTEXT:
        Generic answers aren't helpful
        Need specific info about patient's case
        Context enables personalized responses
    
    Args:
        question: Patient's question
        diagnosis_context: Current diagnosis info
        conversation_history: Previous Q&A turns
        
    Returns:
        Q&A prompt
    """
    
    # Build context section
    context_str = f"""
**DIAGNOSIS CONTEXT:**
- Finding: {diagnosis_context.get('prediction', 'Unknown')}
- Location: {diagnosis_context.get('anatomy', 'Unknown')}
- Confidence: {diagnosis_context.get('confidence', 0):.1%}
"""
    
    # Add conversation history if available
    history_str = ""
    if conversation_history:
        history_str = "\n**PREVIOUS CONVERSATION:**\n"
        for turn in conversation_history[-3:]:  # Last 3 turns
            history_str += f"Q: {turn.get('question', '')}\n"
            history_str += f"A: {turn.get('answer', '')[:100]}...\n\n"
    
    prompt = f"""
{context_str}
{history_str}

**PATIENT QUESTION:**
{question}

**INSTRUCTIONS:**
Provide a helpful, accurate answer that:

1. **ADDRESSES THE QUESTION DIRECTLY**
   - Answer the specific question asked
   - Be clear and specific
   - Use the diagnosis context

2. **PROVIDES MEDICAL INFORMATION**
   - Explain relevant medical concepts
   - Cite general medical knowledge
   - Be evidence-based

3. **IS PATIENT-APPROPRIATE**
   - Use simple, clear language
   - Be empathetic and reassuring
   - Avoid unnecessary medical jargon

4. **INCLUDES SAFETY GUIDELINES**
   - Emphasize consulting with doctor
   - Note AI limitations
   - Recommend professional medical advice for specific decisions

**TONE:**
- Warm and supportive
- Clear and informative
- Professional but accessible
- Honest about uncertainties

**IMPORTANT:**
- Do NOT provide specific medical advice (e.g., exact medications, dosages)
- Do NOT diagnose conditions
- Do NOT replace professional medical consultation
- Always recommend discussing with healthcare provider
"""
    
    return prompt


def generate_treatment_question_prompt(
    question: str,
    fracture_type: str,
    severity: str = 'moderate'
) -> str:
    """
    Generate prompt for treatment-related questions
    
    WHY SEPARATE TREATMENT PROMPTS:
        Treatment questions need specific guidance
        Must emphasize doctor consultation
        Higher risk if misunderstood
    
    Args:
        question: Treatment question
        fracture_type: Type of fracture
        severity: Severity level
        
    Returns:
        Treatment Q&A prompt
    """
    
    prompt = f"""
Answer this treatment question about a {severity} {fracture_type}:

**QUESTION:** {question}

**INSTRUCTIONS:**
Provide general information about treatment options, but:

1. **EXPLAIN GENERAL APPROACHES**
   - Common treatment methods
   - Typical recovery timeline
   - General do's and don'ts

2. **EMPHASIZE INDIVIDUALIZATION**
   - Treatment varies by patient
   - Doctor will determine best approach
   - Many factors affect treatment choice

3. **SAFETY DISCLAIMERS**
   - This is general information only
   - Specific treatment must be determined by doctor
   - Do NOT recommend specific medications or procedures

Be informative but cautious. Always defer to healthcare provider for specific treatment decisions.
"""
    
    return prompt


def generate_recovery_question_prompt(
    question: str,
    diagnosis_context: dict
) -> str:
    """
    Generate prompt for recovery-related questions
    
    WHY RECOVERY PROMPTS:
        Patients very concerned about recovery
        Need realistic expectations
        Important for compliance
    
    Args:
        question: Recovery question
        diagnosis_context: Diagnosis info
        
    Returns:
        Recovery Q&A prompt
    """
    
    prompt = f"""
Answer this recovery question:

**DIAGNOSIS:**
- Type: {diagnosis_context.get('prediction', 'Unknown')}
- Location: {diagnosis_context.get('anatomy', 'Unknown')}

**QUESTION:** {question}

**INSTRUCTIONS:**
Provide helpful recovery information:

1. **TYPICAL TIMELINE**
   - General healing timeframes
   - Stages of recovery
   - What to expect

2. **FACTORS AFFECTING RECOVERY**
   - Age, health, severity
   - Compliance with treatment
   - Activity level

3. **WHAT PATIENT CAN DO**
   - Follow doctor's orders
   - Physical therapy
   - Nutrition, rest

4. **WARNING SIGNS**
   - When to contact doctor
   - Signs of complications
   - Emergency symptoms

Be realistic but encouraging. Emphasize that individual recovery varies.
"""
    
    return prompt


__all__ = [
    'generate_medical_qa_prompt',
    'generate_treatment_question_prompt',
    'generate_recovery_question_prompt'
]
