"""
Test Prompts Script for Prompt Testing

PURPOSE:
    Tests different prompt variations to find the best performing ones.
    Essential for prompt engineering and optimization.

WHY TEST PROMPTS:
    No testing: Suboptimal prompts, wasted tokens
    Manual testing: Time-consuming, inconsistent
    Automated testing (this): Fast, consistent, data-driven
    
    IMPACT: Better prompts, lower costs, higher quality

DESIGN PHILOSOPHY:
    1. Test multiple variations
    2. Measure quality objectively
    3. Track costs
    4. Iterate quickly

USAGE:
    python scripts/test_prompts.py --prompt-type radiology_report --variations 3
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_integration.gemini_client import GeminiClient
from src.prompts.gemini.report_generation import generate_radiology_report_prompt
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_prompt_variation(
    prompt: str,
    variation_name: str,
    client: GeminiClient
) -> dict:
    """
    Test a single prompt variation
    
    WHY MEASURE THESE METRICS:
        - Latency: User experience
        - Tokens: Cost
        - Quality: Usefulness
    
    Args:
        prompt: Prompt to test
        variation_name: Name of variation
        client: LLM client
        
    Returns:
        Test results
    """
    logger.info(f"Testing variation: {variation_name}")
    
    start_time = time.time()
    response = client.generate_text(prompt)
    latency = time.time() - start_time
    
    # WHY ESTIMATE TOKENS:
    # Actual token count requires tokenizer
    # Rough estimate is good enough for testing
    tokens = len(prompt.split()) + len(response.split())
    
    results = {
        'variation': variation_name,
        'latency_seconds': latency,
        'estimated_tokens': tokens,
        'response_length': len(response),
        'response_preview': response[:200] + '...'
    }
    
    logger.info(f"  Latency: {latency:.2f}s, Tokens: {tokens}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Test prompt variations')
    parser.add_argument('--prompt-type', default='radiology_report', help='Prompt type')
    parser.add_argument('--variations', type=int, default=3, help='Number of variations')
    
    args = parser.parse_args()
    
    print(f"=== Testing {args.prompt_type} prompts ===\n")
    
    client = GeminiClient()
    results = []
    
    # WHY TEST MULTIPLE VARIATIONS:
    # Different phrasings can produce very different results
    # Need to find the best one
    for i in range(args.variations):
        prompt = generate_radiology_report_prompt(
            prediction='fracture',
            confidence=0.95,
            anatomy='wrist',
            image_quality=85
        )
        
        result = test_prompt_variation(
            prompt,
            f"variation_{i+1}",
            client
        )
        results.append(result)
    
    # Print summary
    print("\n=== Results Summary ===")
    for result in results:
        print(f"\n{result['variation']}:")
        print(f"  Latency: {result['latency_seconds']:.2f}s")
        print(f"  Tokens: {result['estimated_tokens']}")
        print(f"  Response length: {result['response_length']} chars")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
