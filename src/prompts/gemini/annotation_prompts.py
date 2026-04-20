"""
Gemini Annotation Prompts for Image Annotation Guidance

PURPOSE:
    Generates prompts for guiding annotation of X-ray images.
    Helps create training data and improve model accuracy.

USAGE:
    from src.prompts.gemini.annotation_prompts import generate_annotation_prompt
    
    prompt = generate_annotation_prompt(
        image_type='fracture',
        annotation_task='bounding_box'
    )
"""

def generate_annotation_prompt(
    annotation_task: str = 'bounding_box',
    image_type: str = 'fracture'
) -> str:
    """
    Generate annotation guidance prompt
    
    Args:
        annotation_task: Type of annotation (bounding_box, segmentation, classification)
        image_type: Type of image (fracture, normal)
        
    Returns:
        Annotation prompt
    """
    
    prompts = {
        'bounding_box': """
Identify and describe the location of the fracture for bounding box annotation:

1. **LOCATE FRACTURE**
   - Identify exact fracture location
   - Describe anatomical landmarks
   - Provide coordinates if possible

2. **BOUNDING BOX GUIDANCE**
   - Minimum box that contains fracture
   - Include some surrounding context
   - Ensure fracture is centered

3. **OUTPUT FORMAT**
   - Top-left corner coordinates
   - Width and height
   - Confidence level
""",
        'segmentation': """
Provide detailed fracture segmentation guidance:

1. **FRACTURE BOUNDARIES**
   - Trace exact fracture line
   - Include all fragments
   - Note displacement

2. **SEGMENTATION DETAILS**
   - Pixel-level accuracy
   - Include surrounding affected area
   - Distinguish from normal bone

3. **OUTPUT**
   - Detailed boundary description
   - Key points along fracture line
""",
        'classification': """
Classify this X-ray image:

1. **PRIMARY CLASSIFICATION**
   - Fracture or Normal
   - Confidence level

2. **SECONDARY DETAILS**
   - Fracture type if present
   - Severity assessment
   - Anatomical location

3. **QUALITY ASSESSMENT**
   - Image quality
   - Positioning adequacy
"""
    }
    
    return prompts.get(annotation_task, prompts['classification'])


__all__ = ['generate_annotation_prompt']
