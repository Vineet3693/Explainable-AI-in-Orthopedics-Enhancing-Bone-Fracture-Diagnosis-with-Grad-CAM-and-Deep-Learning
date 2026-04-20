"""
Gemini Multimodal Analysis Prompts

PURPOSE:
    Prompts for Gemini's multimodal capabilities to analyze X-ray images directly.
    Combines image analysis with text generation for comprehensive reports.

WHY MULTIMODAL:
    Text-only: Can't see images, relies on CNN predictions
    Multimodal (this): Analyzes images directly, provides richer insights
    
    IMPACT: More detailed analysis, better quality reports

USAGE:
    from src.prompts.gemini.multimodal_analysis import generate_image_analysis_prompt
    
    prompt = generate_image_analysis_prompt(
        image_path='xray.jpg',
        clinical_context='Wrist pain after fall'
    )
"""

def generate_image_analysis_prompt(
    clinical_context: str = None,
    focus_areas: list = None
) -> str:
    """
    Generate prompt for direct image analysis
    
    WHY DIRECT IMAGE ANALYSIS:
        - Gemini can see the image
        - No need for separate CNN
        - Can provide detailed observations
        - Better for complex cases
    
    Args:
        clinical_context: Patient clinical information
        focus_areas: Specific areas to focus on
        
    Returns:
        Multimodal analysis prompt
    """
    
    prompt = """
Analyze this X-ray image and provide a detailed radiological assessment.

**INSTRUCTIONS:**
1. **SYSTEMATIC REVIEW**
   - Identify the anatomical region
   - Assess image quality and positioning
   - Examine bone structures systematically
   - Look for fractures, dislocations, or abnormalities

2. **DETAILED FINDINGS**
   - Describe any fractures (location, type, displacement)
   - Note alignment and cortical integrity
   - Assess joint spaces
   - Comment on soft tissue if visible

3. **IMPRESSION**
   - Provide clear diagnosis
   - Include confidence level
   - Suggest differential diagnoses if applicable

4. **RECOMMENDATIONS**
   - Additional imaging if needed
   - Clinical correlation
   - Follow-up recommendations

**IMPORTANT:**
- Be specific about anatomical locations
- Quantify findings when possible
- Acknowledge limitations of AI analysis
- Recommend radiologist review
"""
    
    if clinical_context:
        prompt = f"**CLINICAL CONTEXT:** {clinical_context}\n\n" + prompt
    
    if focus_areas:
        areas_str = ", ".join(focus_areas)
        prompt += f"\n\n**FOCUS AREAS:** Pay special attention to: {areas_str}"
    
    return prompt


def generate_comparison_analysis_prompt(
    current_image_description: str = "Current X-ray",
    previous_image_description: str = "Previous X-ray",
    time_interval: str = "unknown"
) -> str:
    """
    Generate prompt for comparing two X-ray images
    
    WHY COMPARISON:
        Track healing progress
        Detect complications
        Monitor treatment effectiveness
    
    Args:
        current_image_description: Description of current image
        previous_image_description: Description of previous image
        time_interval: Time between images
        
    Returns:
        Comparison analysis prompt
    """
    
    prompt = f"""
Compare these two X-ray images taken {time_interval} apart:

**CURRENT IMAGE:** {current_image_description}
**PREVIOUS IMAGE:** {previous_image_description}

**INSTRUCTIONS:**
1. **IDENTIFY CHANGES**
   - Describe what has changed
   - Note improvement, stability, or progression
   - Assess healing progress

2. **HEALING ASSESSMENT**
   - Callus formation (if applicable)
   - Alignment changes
   - Hardware position (if present)

3. **IMPRESSION**
   - Overall healing status
   - Compare with expected timeline
   - Note any complications

4. **RECOMMENDATIONS**
   - Continue current management
   - Modify treatment if needed
   - Follow-up interval

Use comparative language (improved, unchanged, progressed).
"""
    
    return prompt


__all__ = [
    'generate_image_analysis_prompt',
    'generate_comparison_analysis_prompt'
]
