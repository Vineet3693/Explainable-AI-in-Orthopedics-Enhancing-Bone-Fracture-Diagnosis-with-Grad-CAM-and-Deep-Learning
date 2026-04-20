"""
Gemini Report Generation Prompts

PURPOSE:
    Prompt templates for generating professional radiology reports from
    X-ray analysis results. Ensures consistent, high-quality medical reports.

WHY STRUCTURED PROMPTS:
    Ad-hoc prompts: Inconsistent format, missing sections
    Templates (this): Consistent structure, complete reports
    
    IMPACT: Professional-grade reports every time

DESIGN PHILOSOPHY:
    1. Standard medical format (Findings, Impression, Recommendations)
    2. Evidence-based language
    3. Appropriate confidence levels
    4. Safety disclaimers
    5. Actionable recommendations

REPORT SECTIONS:
    - Clinical Information: Patient context
    - Technique: Imaging details
    - Findings: Detailed observations
    - Impression: Summary diagnosis
    - Recommendations: Next steps
    - Disclaimer: AI limitations

USAGE:
    from src.prompts.gemini.report_generation import generate_radiology_report_prompt
    
    prompt = generate_radiology_report_prompt(
        prediction='fracture',
        confidence=0.95,
        anatomy='distal radius',
        image_quality=85
    )
"""

def generate_radiology_report_prompt(
    prediction: str,
    confidence: float,
    anatomy: str,
    image_quality: int,
    patient_age: int = None,
    patient_gender: str = None,
    clinical_history: str = None
) -> str:
    """
    Generate prompt for radiology report
    
    WHY FUNCTION NOT CONSTANT:
        Need to inject specific patient data
        Each report is unique
        Dynamic content based on findings
    
    Args:
        prediction: AI prediction (fracture/normal)
        confidence: Prediction confidence (0-1)
        anatomy: Bone/body part
        image_quality: Quality score (0-100)
        patient_age: Patient age (optional)
        patient_gender: Patient gender (optional)
        clinical_history: Clinical context (optional)
        
    Returns:
        Formatted prompt string
    """
    
    # WHY INCLUDE PATIENT DEMOGRAPHICS:
    # Age affects bone density, healing
    # Gender affects fracture patterns
    # History provides context
    patient_info = ""
    if patient_age:
        patient_info += f"Age: {patient_age} years\n"
    if patient_gender:
        patient_info += f"Gender: {patient_gender}\n"
    if clinical_history:
        patient_info += f"Clinical History: {clinical_history}\n"
    
    prompt = f"""
Generate a professional radiology report for the following X-ray analysis:

**IMAGING ANALYSIS RESULTS:**
- AI Prediction: {prediction.upper()}
- Confidence Level: {confidence:.1%}
- Anatomical Location: {anatomy}
- Image Quality Score: {image_quality}/100

{f"**PATIENT INFORMATION:**\n{patient_info}" if patient_info else ""}

**INSTRUCTIONS:**
Please generate a comprehensive radiology report following standard medical format. Include the following sections:

1. **CLINICAL INFORMATION**
   - Briefly state the clinical indication
   - Note patient demographics if provided
   - Mention any relevant history

2. **TECHNIQUE**
   - Imaging modality (X-ray)
   - Views obtained
   - Image quality assessment

3. **FINDINGS**
   - Detailed description of bone structures
   - Specific observations about the {anatomy}
   - Note any abnormalities or fractures
   - Describe alignment, cortical integrity, joint spaces
   - Comment on soft tissue if visible

4. **IMPRESSION**
   - Concise summary of key findings
   - State the diagnosis clearly
   - Include confidence level: {confidence:.1%}
   - Note if findings are consistent with clinical history

5. **RECOMMENDATIONS**
   - Suggest follow-up imaging if needed
   - Recommend clinical correlation
   - Advise on urgent vs routine follow-up
   - Mention any additional studies that may be helpful

6. **AI ANALYSIS DISCLAIMER**
   - State that this is AI-assisted analysis
   - Emphasize need for radiologist review
   - Note AI confidence level
   - Recommend professional verification

**IMPORTANT GUIDELINES:**
- Use standard medical terminology
- Be specific about anatomical locations
- Quantify findings when possible (e.g., "2mm displacement")
- Acknowledge uncertainty when present
- Maintain professional, objective tone
- Include appropriate medical disclaimers

**OUTPUT FORMAT:**
Return the report in a structured format with clear section headings.
Use professional medical language appropriate for radiologist review.
"""
    
    return prompt


def generate_comparison_report_prompt(
    current_findings: dict,
    previous_findings: dict,
    time_interval: str
) -> str:
    """
    Generate prompt for comparison report (current vs previous)
    
    WHY COMPARISON REPORTS:
        Track healing progress
        Detect complications
        Monitor treatment effectiveness
    
    Args:
        current_findings: Current X-ray results
        previous_findings: Previous X-ray results
        time_interval: Time between studies
        
    Returns:
        Comparison report prompt
    """
    
    prompt = f"""
Generate a comparison radiology report analyzing changes between two X-ray studies:

**CURRENT STUDY:**
- Date: {current_findings.get('date', 'Current')}
- Prediction: {current_findings.get('prediction', 'Unknown')}
- Confidence: {current_findings.get('confidence', 0):.1%}
- Anatomy: {current_findings.get('anatomy', 'Unknown')}

**PREVIOUS STUDY:**
- Date: {previous_findings.get('date', 'Previous')}
- Prediction: {previous_findings.get('prediction', 'Unknown')}
- Confidence: {previous_findings.get('confidence', 0):.1%}

**TIME INTERVAL:** {time_interval}

**INSTRUCTIONS:**
Generate a comparison report that includes:

1. **COMPARISON FINDINGS**
   - Describe changes since previous study
   - Note improvement, stability, or progression
   - Comment on healing progress if fracture present
   - Assess alignment changes
   - Evaluate callus formation (if applicable)

2. **IMPRESSION**
   - Summarize key changes
   - Assess healing status
   - Note any complications
   - Compare with expected healing timeline

3. **RECOMMENDATIONS**
   - Suggest continued management
   - Recommend follow-up interval
   - Note if treatment modification needed
   - Advise on activity restrictions

Use comparative language (e.g., "improved", "unchanged", "progressed").
Provide specific measurements when comparing findings.
"""
    
    return prompt


def generate_teaching_report_prompt(
    findings: dict,
    educational_level: str = 'medical_student'
) -> str:
    """
    Generate educational report with teaching points
    
    WHY TEACHING MODE:
        Train medical students
        Explain findings in detail
        Highlight learning points
    
    Args:
        findings: X-ray analysis results
        educational_level: Target audience level
        
    Returns:
        Educational report prompt
    """
    
    prompt = f"""
Generate an educational radiology report for {educational_level} level:

**CASE FINDINGS:**
- Prediction: {findings.get('prediction', 'Unknown')}
- Anatomy: {findings.get('anatomy', 'Unknown')}
- Confidence: {findings.get('confidence', 0):.1%}

**INSTRUCTIONS:**
Create a teaching-focused report that includes:

1. **SYSTEMATIC APPROACH**
   - Demonstrate step-by-step analysis
   - Explain what to look for
   - Describe normal anatomy first
   - Then identify abnormalities

2. **DETAILED FINDINGS**
   - Explain each observation
   - Use anatomical landmarks
   - Describe radiographic signs
   - Include differential diagnosis

3. **TEACHING POINTS**
   - Key learning objectives
   - Common pitfalls to avoid
   - Clinical correlations
   - Relevant anatomy review

4. **CLINICAL SIGNIFICANCE**
   - Why these findings matter
   - Treatment implications
   - Prognosis discussion
   - Follow-up considerations

Make it educational and detailed, explaining the "why" behind observations.
Include relevant medical knowledge and context.
"""
    
    return prompt


__all__ = [
    'generate_radiology_report_prompt',
    'generate_comparison_report_prompt',
    'generate_teaching_report_prompt'
]
