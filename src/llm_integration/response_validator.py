"""
Response Validator for LLM Outputs

PURPOSE:
    Validates LLM responses for quality, safety, and medical accuracy.
    Catches hallucinations, inappropriate content, and medical errors.

WHY RESPONSE VALIDATOR:
    Raw LLM output: May contain errors, hallucinations
    Validator (this): Quality checks, safety filters
    
    IMPACT: Safer medical AI, fewer errors

DESIGN PHILOSOPHY:
    1. Safety-first (medical accuracy critical)
    2. Multi-layer validation (structure, content, medical)
    3. Clear rejection reasons
    4. Configurable strictness

PROS:
    ✅ Catches hallucinations
    ✅ Medical safety checks
    ✅ Inappropriate content filtering
    ✅ Configurable rules

CONS:
    ❌ May reject valid responses
    ❌ Requires medical knowledge base
    ❌ Adds latency

USAGE:
    from src.llm_integration.response_validator import ResponseValidator
    
    validator = ResponseValidator()
    is_valid, issues = validator.validate(
        response,
        response_type='radiology_report'
    )
"""

import re
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Validates LLM responses for quality and safety"""
    
    def __init__(self):
        """Initialize validator"""
        # WHY FORBIDDEN PHRASES:
        # LLMs sometimes generate inappropriate content
        # Medical AI must be professional
        self.forbidden_phrases = [
            'i am not a doctor',
            'i cannot provide medical advice',
            'consult a healthcare professional',  # Too generic
            'i don\'t know',
            'as an ai'
        ]
        
        # WHY REQUIRED ELEMENTS:
        # Medical reports must have certain sections
        # Ensures completeness
        self.required_elements = {
            'radiology_report': ['findings', 'impression'],
            'patient_summary': ['diagnosis', 'recommendations']
        }
        
        logger.info("Initialized ResponseValidator")
    
    def validate(
        self,
        response: str,
        response_type: str = 'general',
        strict: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate LLM response
        
        WHY MULTI-LAYER VALIDATION:
            Different types of errors
            Comprehensive quality check
            Clear error reporting
        
        Args:
            response: LLM response text
            response_type: Type of response
            strict: If True, apply stricter rules
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check 1: Empty or too short
        # WHY CHECK LENGTH:
        # Empty responses are useless
        # Too short may be incomplete
        if not response or len(response.strip()) < 10:
            issues.append("Response is empty or too short")
            return False, issues
        
        # Check 2: Forbidden phrases
        # WHY CHECK PHRASES:
        # Catches LLM disclaimers
        # Ensures professional tone
        for phrase in self.forbidden_phrases:
            if phrase.lower() in response.lower():
                issues.append(f"Contains forbidden phrase: '{phrase}'")
        
        # Check 3: Required elements
        # WHY CHECK ELEMENTS:
        # Ensures response completeness
        # Medical reports need specific sections
        if response_type in self.required_elements:
            for element in self.required_elements[response_type]:
                if element.lower() not in response.lower():
                    issues.append(f"Missing required element: '{element}'")
        
        # Check 4: Medical accuracy indicators
        # WHY CHECK ACCURACY:
        # Catch potential hallucinations
        # Medical AI must be accurate
        accuracy_issues = self._check_medical_accuracy(response)
        issues.extend(accuracy_issues)
        
        # Check 5: Inappropriate content
        # WHY CHECK CONTENT:
        # Medical AI must be professional
        # Patient safety
        content_issues = self._check_inappropriate_content(response)
        issues.extend(content_issues)
        
        # Determine validity
        # WHY STRICT MODE:
        # Production: Any issue is failure
        # Development: Minor issues acceptable
        if strict:
            is_valid = len(issues) == 0
        else:
            # Allow minor issues in non-strict mode
            critical_keywords = ['forbidden', 'inappropriate', 'hallucination']
            critical_issues = [
                issue for issue in issues
                if any(keyword in issue.lower() for keyword in critical_keywords)
            ]
            is_valid = len(critical_issues) == 0
        
        if not is_valid:
            logger.warning(f"Response validation failed: {issues}")
        
        return is_valid, issues
    
    def _check_medical_accuracy(self, response: str) -> List[str]:
        """
        Check for medical accuracy issues
        
        WHY CHECK ACCURACY:
            LLMs can hallucinate medical facts
            Critical for patient safety
            Need to catch obvious errors
        
        Args:
            response: Response text
            
        Returns:
            List of accuracy issues
        """
        issues = []
        
        # Check for contradictions
        # WHY CHECK CONTRADICTIONS:
        # "fracture present" and "no fracture" in same response
        # Indicates hallucination or confusion
        if 'fracture' in response.lower() and 'no fracture' in response.lower():
            # Check if they're in different contexts
            if 'fracture present' in response.lower() and 'no fracture detected' in response.lower():
                issues.append("Potential contradiction: mentions both fracture and no fracture")
        
        # Check for unrealistic values
        # WHY CHECK VALUES:
        # Catch obviously wrong numbers
        # E.g., "150% confidence" or "300 degree angle"
        percent_pattern = r'(\d+)%'
        percentages = re.findall(percent_pattern, response)
        for pct in percentages:
            if int(pct) > 100:
                issues.append(f"Unrealistic percentage: {pct}%")
        
        return issues
    
    def _check_inappropriate_content(self, response: str) -> List[str]:
        """
        Check for inappropriate content
        
        WHY CHECK CONTENT:
            Professional medical communication
            Patient safety and trust
            Regulatory compliance
        
        Args:
            response: Response text
            
        Returns:
            List of content issues
        """
        issues = []
        
        # Check for overly casual language
        # WHY CHECK TONE:
        # Medical reports should be professional
        # Builds trust with healthcare providers
        casual_phrases = ['lol', 'omg', 'btw', 'tbh']
        for phrase in casual_phrases:
            if phrase in response.lower():
                issues.append(f"Inappropriate casual language: '{phrase}'")
        
        # Check for absolute certainty (red flag)
        # WHY CHECK CERTAINTY:
        # Medical AI should express appropriate uncertainty
        # "100% certain" is rarely appropriate
        absolute_phrases = ['100% certain', 'definitely', 'absolutely no doubt']
        for phrase in absolute_phrases:
            if phrase.lower() in response.lower():
                issues.append(f"Inappropriate absolute certainty: '{phrase}'")
        
        return issues


__all__ = ['ResponseValidator']
