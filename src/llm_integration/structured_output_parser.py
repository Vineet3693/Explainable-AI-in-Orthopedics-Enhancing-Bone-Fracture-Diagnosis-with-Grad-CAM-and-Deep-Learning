"""
Structured Output Parser for LLM Responses

PURPOSE:
    Parses and validates structured outputs from LLMs (JSON responses).
    Ensures LLM responses match expected schema and handles parsing errors.

WHY STRUCTURED OUTPUT PARSER:
    Raw LLM output: Unpredictable format, may have errors
    Parser (this): Validates, cleans, provides fallbacks
    
    IMPACT: Reliable LLM integration, fewer crashes

DESIGN PHILOSOPHY:
    1. Robust parsing (handle malformed JSON)
    2. Schema validation (Pydantic models)
    3. Error recovery (fallbacks, retries)
    4. Clear error messages

PROS:
    ✅ Handles malformed JSON
    ✅ Schema validation
    ✅ Clear error messages
    ✅ Fallback mechanisms

CONS:
    ❌ Adds processing overhead
    ❌ May hide LLM issues
    ❌ Requires schema definitions

USAGE:
    from src.llm_integration.structured_output_parser import StructuredOutputParser
    from src.prompts.structured_outputs import RadiologyReport
    
    parser = StructuredOutputParser()
    report = parser.parse(
        llm_response,
        schema=RadiologyReport
    )
"""

import json
import re
from typing import Any, Type, Optional, TypeVar
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class StructuredOutputParser:
    """Parser for structured LLM outputs"""
    
    def __init__(self):
        """Initialize parser"""
        logger.info("Initialized StructuredOutputParser")
    
    def parse(
        self,
        llm_output: str,
        schema: Type[T],
        strict: bool = False
    ) -> Optional[T]:
        """
        Parse LLM output into Pydantic model
        
        WHY MULTI-STEP PARSING:
            LLMs may wrap JSON in markdown
            May include extra text
            Need to extract and clean JSON
        
        Args:
            llm_output: Raw LLM response
            schema: Pydantic model class
            strict: If True, raise on validation errors
            
        Returns:
            Parsed model instance or None
        """
        try:
            # Step 1: Extract JSON from response
            # WHY EXTRACT:
            # LLMs often wrap JSON in ```json ... ```
            # Need to extract the actual JSON
            json_str = self._extract_json(llm_output)
            
            # Step 2: Parse JSON
            # WHY TRY-EXCEPT:
            # JSON may still be malformed
            # Provide clear error message
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.debug(f"Attempted to parse: {json_str[:200]}")
                if strict:
                    raise
                return None
            
            # Step 3: Validate with Pydantic
            # WHY PYDANTIC:
            # Type validation
            # Data coercion
            # Clear error messages
            try:
                return schema(**data)
            except ValidationError as e:
                logger.error(f"Validation error: {e}")
                if strict:
                    raise
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error parsing output: {e}")
            if strict:
                raise
            return None
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text
        
        WHY REGEX:
            LLMs wrap JSON in various ways
            Need flexible extraction
        
        PATTERNS:
            ```json ... ```
            ```{ ... }```
            { ... }
        
        Args:
            text: Text containing JSON
            
        Returns:
            Extracted JSON string
        """
        # Try to find JSON in code blocks
        # WHY THIS PATTERN:
        # Matches ```json ... ``` or ```{ ... }```
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(code_block_pattern, text, re.DOTALL)
        
        if match:
            return match.group(1)
        
        # Try to find raw JSON object
        # WHY THIS PATTERN:
        # Matches { ... } with proper nesting
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            return match.group(0)
        
        # Return original if no pattern matched
        # WHY RETURN ORIGINAL:
        # Let JSON parser handle it
        # May still be valid JSON
        return text.strip()
    
    def parse_with_fallback(
        self,
        llm_output: str,
        schema: Type[T],
        fallback_values: dict
    ) -> T:
        """
        Parse with fallback values
        
        WHY FALLBACK:
            Production systems need reliability
            Better to have partial data than crash
            Can log and alert on fallback usage
        
        Args:
            llm_output: Raw LLM response
            schema: Pydantic model class
            fallback_values: Default values if parsing fails
            
        Returns:
            Parsed model or model with fallback values
        """
        result = self.parse(llm_output, schema, strict=False)
        
        if result is None:
            logger.warning(f"Parsing failed, using fallback values")
            return schema(**fallback_values)
        
        return result


__all__ = ['StructuredOutputParser']
