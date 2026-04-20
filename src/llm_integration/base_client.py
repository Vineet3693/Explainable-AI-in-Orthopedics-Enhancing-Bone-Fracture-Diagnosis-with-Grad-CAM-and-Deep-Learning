"""
Base LLM Client

PURPOSE:
    Abstract base class for all LLM clients.
    Defines the standard interface for text generation and structured outputs.

WHY BASE CLIENT:
    Polymorphism: Swap providers easily (Gemini <-> Groq).
    Consistency: Ensure all clients implement required methods.

USAGE:
    # Subclass BaseLLMClient
    class MyClient(BaseLLMClient):
        def generate_text(self, prompt): ...
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Generator

class BaseLLMClient(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate simple text response

        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Creativity parameter
            max_tokens: Max output length

        Returns:
            Generated text string
        """
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_model: Any,
        system_prompt: Optional[str] = None
    ) -> Any:
        """
        Generate structured output (Pydantic model)

        Args:
            prompt: User prompt
            response_model: Pydantic model class
            system_prompt: System instruction

        Returns:
            Instance of response_model
        """
        pass

    @abstractmethod
    def stream_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream text response chunks

        Args:
            prompt: User prompt
            system_prompt: System instruction

        Yields:
            Text chunks
        """
        pass


__all__ = ['BaseLLMClient']
