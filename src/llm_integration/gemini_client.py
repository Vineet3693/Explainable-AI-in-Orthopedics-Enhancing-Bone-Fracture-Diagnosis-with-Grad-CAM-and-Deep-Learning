"""
Gemini Client implementation

PURPOSE:
    Implementation of Gemini LLM client.
    Handles authentication, request formatting, and response parsing.

WHY OVERRIDE:
    Gemini has specific API structures (generativeai library).

USAGE:
    client = GeminiClient(api_key="...")
    response = client.generate_text("Hello")
"""

import os
import logging
from typing import Optional, Any, Generator, Dict
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.config import MAX_TOKENS, TEMPERATURE
from src.llm_integration.base_client import BaseLLMClient
from src.llm_integration.retry_logic import with_retry

logger = logging.getLogger(__name__)


class GeminiClient(BaseLLMClient):
    """Gemini API Client"""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro"):
        """
        Initialize Gemini client

        Args:
            api_key: Gemini API Key (defaults to env var)
            model_name: Model to use
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Client will fail if called.")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        
        # Safety settings (allow medical content)
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

    @with_retry(max_retries=3)
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate text using Gemini"""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt
        )
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )

        try:
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    @with_retry(max_retries=3)
    def generate_structured(
        self,
        prompt: str,
        response_model: Any,
        system_prompt: Optional[str] = None
    ) -> Any:
        """
        Generate structured output.
        Note: Native JSON mode validation in Gemini is evolving.
        We use raw generation + Pydantic validation for broad compatibility.
        """
        # Append instruction to output JSON
        json_prompt = f"{prompt}\n\nIMPORTANT: Output strictly in valid JSON format matching this schema: {response_model.schema_json()}"
        
        text_response = self.generate_text(
            prompt=json_prompt,
            system_prompt=system_prompt,
            temperature=0.0 # Strict for JSON
        )
        
        try:
            # Simple cleanup for markdown code blocks
            cleaned_text = text_response.replace("```json", "").replace("```", "").strip()
            return response_model.parse_raw(cleaned_text)
        except Exception as e:
            logger.error(f"Failed to parse structured output: {e}")
            logger.debug(f"Raw output: {text_response}")
            raise

    def stream_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream response"""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt
        )
        
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text


__all__ = ['GeminiClient']
