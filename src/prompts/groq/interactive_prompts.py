"""
Groq Interactive Prompts for Conversational Q&A

PURPOSE:
    Interactive conversation prompts for multi-turn Q&A sessions.
    Maintains context across conversation for better answers.

USAGE:
    from src.prompts.groq.interactive_prompts import generate_conversation_prompt
    
    prompt = generate_conversation_prompt(
        question='What about recovery time?',
        conversation_history=[...]
    )
"""

from typing import List, Dict


def generate_conversation_prompt(
    question: str,
    conversation_history: List[Dict[str, str]],
    diagnosis_context: Dict[str, any] = None
) -> str:
    """
    Generate conversational Q&A prompt
    
    WHY CONVERSATION HISTORY:
        Maintains context across turns
        Enables follow-up questions
        More natural interaction
    
    Args:
        question: Current question
        conversation_history: Previous Q&A turns
        diagnosis_context: Diagnosis information
        
    Returns:
        Conversation prompt
    """
    
    prompt = "You are a helpful medical AI assistant answering questions about fractures.\n\n"
    
    # Add diagnosis context
    if diagnosis_context:
        prompt += f"**DIAGNOSIS:**\n"
        prompt += f"- Finding: {diagnosis_context.get('prediction', 'Unknown')}\n"
        prompt += f"- Location: {diagnosis_context.get('anatomy', 'Unknown')}\n\n"
    
    # Add conversation history
    if conversation_history:
        prompt += "**CONVERSATION HISTORY:**\n"
        for turn in conversation_history[-3:]:  # Last 3 turns
            prompt += f"User: {turn.get('question', '')}\n"
            prompt += f"Assistant: {turn.get('answer', '')}\n\n"
    
    # Add current question
    prompt += f"**CURRENT QUESTION:**\n{question}\n\n"
    
    prompt += """
**INSTRUCTIONS:**
- Answer the question directly
- Use context from previous conversation
- Be concise (2-3 sentences)
- Include medical disclaimer if needed
"""
    
    return prompt


def generate_clarification_prompt(
    unclear_question: str
) -> str:
    """
    Generate prompt for clarifying unclear questions
    
    WHY CLARIFICATION:
        Unclear questions lead to poor answers
        Better to ask for clarification
        
    Args:
        unclear_question: Question that needs clarification
        
    Returns:
        Clarification prompt
    """
    
    prompt = f"""
The user asked: "{unclear_question}"

This question is unclear or ambiguous. Generate 2-3 clarifying questions to better understand what the user wants to know.

**EXAMPLES:**
- "What specific aspect are you asking about?"
- "Are you asking about [option A] or [option B]?"
- "Could you provide more context about...?"

Be helpful and guide the user to ask a clearer question.
"""
    
    return prompt


__all__ = [
    'generate_conversation_prompt',
    'generate_clarification_prompt'
]
