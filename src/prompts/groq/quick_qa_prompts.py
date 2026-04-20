"""
Groq Quick Q&A Prompts for Fast Responses

PURPOSE:
    Ultra-fast question answering prompts optimized for Groq's speed.
    Provides instant responses to common fracture-related questions.

WHY GROQ FOR Q&A:
    Gemini: 2-3 seconds, better for complex questions
    Groq: <1 second, perfect for simple Q&A
    
    IMPACT: 10x faster responses, better user experience

DESIGN PHILOSOPHY:
    1. Speed optimized (minimal tokens)
    2. Direct answers (no fluff)
    3. Concise (2-3 sentences)
    4. Actionable (clear guidance)

PROS:
    ✅ Sub-second response time
    ✅ Very low cost
    ✅ Good for simple questions
    ✅ Consistent format

CONS:
    ❌ Less detailed than Gemini
    ❌ May oversimplify complex topics
    ❌ Text-only (no image analysis)

USAGE:
    from src.prompts.groq.quick_qa_prompts import generate_quick_qa_prompt
    
    prompt = generate_quick_qa_prompt(
        question='How long does recovery take?',
        context={'diagnosis': 'wrist fracture'}
    )
"""

def generate_quick_qa_prompt(
    question: str,
    context: dict = None
) -> str:
    """
    Generate prompt for quick Q&A
    
    WHY MINIMAL CONTEXT:
        Groq is fast but has smaller context window
        Keep prompts concise for speed
        Focus on essential information only
    
    Args:
        question: User's question
        context: Optional context (diagnosis, etc.)
        
    Returns:
        Quick Q&A prompt
    """
    
    context_str = ""
    if context:
        if 'diagnosis' in context:
            context_str += f"Diagnosis: {context['diagnosis']}\n"
        if 'anatomy' in context:
            context_str += f"Location: {context['anatomy']}\n"
    
    prompt = f"""
{f"Context:\n{context_str}" if context_str else ""}
Question: {question}

Provide a brief, clear answer (2-3 sentences max).
Be direct and actionable.
Include disclaimer if medical advice.
"""
    
    return prompt


def generate_yes_no_prompt(question: str) -> str:
    """
    Generate prompt for yes/no questions
    
    WHY YES/NO:
        Fastest possible response
        Clear, unambiguous
        Perfect for simple queries
    
    Args:
        question: Yes/no question
        
    Returns:
        Yes/no prompt
    """
    
    prompt = f"""
Answer this yes/no question about fractures:

{question}

Provide:
1. Yes or No
2. One sentence explanation
3. Disclaimer if needed

Be concise and clear.
"""
    
    return prompt


def generate_list_prompt(question: str, max_items: int = 5) -> str:
    """
    Generate prompt for list-based answers
    
    WHY LISTS:
        Easy to scan
        Clear structure
        Actionable items
    
    Args:
        question: Question requiring list answer
        max_items: Maximum list items
        
    Returns:
        List prompt
    """
    
    prompt = f"""
{question}

Provide a bulleted list (max {max_items} items).
Be specific and actionable.
Keep each point to one line.
"""
    
    return prompt


__all__ = [
    'generate_quick_qa_prompt',
    'generate_yes_no_prompt',
    'generate_list_prompt'
]
