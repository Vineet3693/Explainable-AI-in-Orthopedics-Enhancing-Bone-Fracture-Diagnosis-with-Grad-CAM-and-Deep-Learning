"""
Gemini Validation Prompts for Quality Assessment

PURPOSE:
    Prompts for validating X-ray image quality and suitability for analysis.
    Helps ensure only high-quality images are processed.

USAGE:
    from src.prompts.gemini.validation_prompts import generate_quality_check_prompt
    
    prompt = generate_quality_check_prompt()
"""

def generate_quality_check_prompt() -> str:
    """
    Generate image quality validation prompt
    
    WHY QUALITY CHECKS:
        Poor quality images lead to incorrect diagnoses
        Better to reject than misdiagnose
        
    Returns:
        Quality check prompt
    """
    
    prompt = """
Assess the quality and suitability of this X-ray image for fracture detection:

**QUALITY CRITERIA:**

1. **TECHNICAL QUALITY**
   - Adequate exposure (not too dark/bright)
   - Minimal blur or motion artifacts
   - Appropriate contrast
   - No significant noise

2. **POSITIONING**
   - Correct anatomical positioning
   - Adequate coverage of region of interest
   - Proper alignment
   - No rotation artifacts

3. **DIAGNOSTIC VALUE**
   - Key anatomical structures visible
   - Fracture would be detectable if present
   - No obstructions (jewelry, clothing)

4. **OVERALL ASSESSMENT**
   - Rate quality: Excellent/Good/Fair/Poor
   - Suitable for AI analysis: Yes/No
   - Specific issues if any
   - Recommendations for improvement

**OUTPUT:**
Provide quality score (0-100) and suitability assessment.
"""
    
    return prompt


def generate_xray_verification_prompt() -> str:
    """
    Generate prompt to verify image is an X-ray
    
    WHY VERIFY:
        Users might upload wrong image type
        Need to confirm it's actually an X-ray
        
    Returns:
        Verification prompt
    """
    
    prompt = """
Verify if this image is a valid X-ray radiograph:

**VERIFICATION CHECKS:**

1. **IMAGE TYPE**
   - Is this an X-ray image?
   - If not, what type of image is it?

2. **ANATOMICAL REGION**
   - What body part is shown?
   - Is it a bone/skeletal X-ray?

3. **MODALITY**
   - Confirm it's X-ray (not CT, MRI, ultrasound)
   - Check for typical X-ray characteristics

**OUTPUT:**
- Is valid X-ray: Yes/No
- Anatomical region: [region]
- Confidence: [0-1]
- Issues if any
"""
    
    return prompt


__all__ = [
    'generate_quality_check_prompt',
    'generate_xray_verification_prompt'
]
