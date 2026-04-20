"""
LLM Logger for LLM Interaction Logging

PURPOSE:
    Logs all LLM API calls with prompts, responses, and costs.
    Essential for prompt optimization and cost tracking.

WHY LLM LOGGING:
    Debug prompts, track costs, optimize performance
    
    IMPACT: Better prompts, cost control, debugging

USAGE:
    from src.monitoring.logging.llm_logger import LLMLogger
    
    logger = LLMLogger()
    logger.log_llm_call(
        provider='gemini',
        prompt='Analyze this X-ray...',
        response='The X-ray shows...',
        tokens=500,
        cost=0.001
    )
"""

import json
import logging
from datetime import datetime
from typing import Optional
import os
import hashlib

logger = logging.getLogger(__name__)


class LLMLogger:
    """LLM interaction logger"""
    
    def __init__(self, log_dir: str = 'logs/llm'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_llm_call(
        self,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        tokens: int,
        cost: float,
        latency: float,
        success: bool = True,
        error: Optional[str] = None,
        anonymize: bool = True
    ):
        """
        Log LLM API call
        
        WHY LOG LLM CALLS:
            - Debug prompt issues
            - Track API costs
            - Optimize prompts
            - Monitor performance
            - Detect quality issues
        
        Args:
            provider: LLM provider (gemini, groq)
            model: Model name
            prompt: Input prompt
            response: LLM response
            tokens: Total tokens used
            cost: Cost in USD
            latency: Response time in seconds
            success: Whether call succeeded
            error: Error message if failed
            anonymize: Whether to anonymize PHI
        """
        # WHY ANONYMIZE BY DEFAULT:
        # Prompts may contain PHI
        # HIPAA requires anonymization
        if anonymize:
            prompt = self._anonymize_phi(prompt)
            response = self._anonymize_phi(response)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'prompt_hash': hashlib.md5(prompt.encode()).hexdigest(),
            'prompt_length': len(prompt),
            'response_length': len(response),
            'tokens': tokens,
            'cost_usd': cost,
            'latency_seconds': latency,
            'success': success,
            'error': error
        }
        
        # WHY HASH INSTEAD OF FULL PROMPT:
        # Save space, protect PHI
        # Can still identify duplicate prompts
        
        # Write to daily log file
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.log_dir, f'{provider}_calls_{date_str}.jsonl')
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.debug(
            f"LLM call: {provider}/{model} - {tokens} tokens - ${cost:.4f} - {latency:.2f}s"
        )
    
    def _anonymize_phi(self, text: str) -> str:
        """Anonymize PHI in text"""
        # Simple placeholder - real implementation would use NER
        return text  # TODO: Implement proper PHI anonymization


__all__ = ['LLMLogger']
