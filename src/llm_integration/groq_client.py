"""
Groq Client implementation

PURPOSE:
    Implementation of Groq LLM client for ultra-fast inference.

WHY GROQ:
    Speed: >300 tokens/sec.
    Ideal for real-time Q&A and urgent summaries.

USAGE:
    client = GroqClient(api_key="...")
    response = client.generate_text("Hello")
"""

import os
import logging
from typing import Optional, Any, Generator
import groq

from src.llm_integration.base_client import BaseLLMClient
from src.llm_integration.retry_logic import with_retry

logger = logging.getLogger(__name__)


class GroqClient(BaseLLMClient):
    """Groq API Client"""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "llama3-70b-8192"):
        """
        Initialize Groq client

        Args:
            api_key: Groq API Key
            model_name: Model to use (default: Llama3 70B)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found. Client will fail if called.")
        
        self.client = groq.Groq(api_key=self.api_key)
        self.model_name = model_name

    @with_retry(max_retries=3)
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate text using Groq"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise

    @with_retry(max_retries=3)
    def generate_structured(
        self,
        prompt: str,
        response_model: Any,
        system_prompt: Optional[str] = None
    ) -> Any:
        """Generate structured output using Groq JSON mode"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Append schema requirement
        json_prompt = f"{prompt}\n\nReturn the response as a valid JSON object matching this schema: {response_model.schema_json()}"
        messages.append({"role": "user", "content": json_prompt})

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.0, # Deterministic
                response_format={"type": "json_object"} # Enable JSON mode
            )
            json_content = chat_completion.choices[0].message.content
            return response_model.parse_raw(json_content)
        except Exception as e:
            logger.error(f"Groq structured generation failed: {e}")
            raise

    def stream_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream response"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            stream=True
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content


__all__ = ['GroqClient']
