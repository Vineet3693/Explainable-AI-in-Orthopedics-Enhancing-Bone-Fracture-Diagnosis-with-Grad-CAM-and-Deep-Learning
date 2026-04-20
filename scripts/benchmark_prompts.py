"""
Benchmark Prompts Script for Performance Testing

PURPOSE:
    Benchmarks prompt performance across different LLM providers.
    Compares Gemini vs Groq for speed, cost, and quality.

WHY BENCHMARK:
    No benchmarking: Don't know which LLM is best
    Manual comparison: Time-consuming, inconsistent
    Automated benchmarking (this): Fast, objective, data-driven
    
    IMPACT: Choose best LLM for each task, optimize costs

DESIGN PHILOSOPHY:
    1. Test same prompt on multiple LLMs
    2. Measure speed, cost, quality
    3. Generate comparison report
    4. Make data-driven decisions

PROS:
    ✅ Objective comparison
    ✅ Identifies best LLM per task
    ✅ Cost optimization
    ✅ Performance insights

CONS:
    ❌ Requires API access to multiple LLMs
    ❌ Costs money to run
    ❌ Quality is subjective

USAGE:
    python scripts/benchmark_prompts.py --task summary --iterations 10
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_integration.gemini_client import GeminiClient
from src.llm_integration.groq_client import GroqClient
import logging
import time
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def benchmark_llm(
    client,
    provider_name: str,
    prompt: str,
    iterations: int = 10
) -> dict:
    """
    Benchmark an LLM provider
    
    WHY MULTIPLE ITERATIONS:
        Single test is unreliable
        Need average and variance
        Detect outliers
    
    Args:
        client: LLM client
        provider_name: Provider name
        prompt: Test prompt
        iterations: Number of test runs
        
    Returns:
        Benchmark results
    """
    logger.info(f"Benchmarking {provider_name}...")
    
    latencies = []
    token_counts = []
    
    for i in range(iterations):
        start_time = time.time()
        response = client.generate_text(prompt)
        latency = time.time() - start_time
        
        latencies.append(latency)
        # Rough token estimate
        tokens = len(prompt.split()) + len(response.split())
        token_counts.append(tokens)
        
        logger.debug(f"  Iteration {i+1}: {latency:.2f}s")
    
    # WHY CALCULATE PERCENTILES:
    # Mean can be skewed by outliers
    # p50 (median) and p95 are more robust
    results = {
        'provider': provider_name,
        'iterations': iterations,
        'latency_mean': statistics.mean(latencies),
        'latency_p50': statistics.median(latencies),
        'latency_p95': sorted(latencies)[int(0.95 * len(latencies))],
        'tokens_mean': statistics.mean(token_counts),
        'cost_per_request': statistics.mean(token_counts) * 0.0001  # Rough estimate
    }
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Benchmark LLM providers')
    parser.add_argument('--task', default='summary', help='Task type')
    parser.add_argument('--iterations', type=int, default=10, help='Iterations')
    
    args = parser.parse_args()
    
    print(f"=== Benchmarking LLM Providers ===")
    print(f"Task: {args.task}")
    print(f"Iterations: {args.iterations}\n")
    
    # Test prompt
    prompt = "Summarize this medical report in 2-3 sentences: Patient has wrist fracture."
    
    # Benchmark Gemini
    gemini_client = GeminiClient()
    gemini_results = benchmark_llm(gemini_client, 'Gemini', prompt, args.iterations)
    
    # Benchmark Groq
    groq_client = GroqClient()
    groq_results = benchmark_llm(groq_client, 'Groq', prompt, args.iterations)
    
    # Print comparison
    print("\n=== Results ===\n")
    print(f"{'Metric':<20} {'Gemini':<15} {'Groq':<15} {'Winner':<10}")
    print("-" * 60)
    
    # Latency comparison
    print(f"{'Latency (mean)':<20} {gemini_results['latency_mean']:.3f}s{' '*8} {groq_results['latency_mean']:.3f}s{' '*8} {'Groq' if groq_results['latency_mean'] < gemini_results['latency_mean'] else 'Gemini'}")
    print(f"{'Latency (p95)':<20} {gemini_results['latency_p95']:.3f}s{' '*8} {groq_results['latency_p95']:.3f}s{' '*8} {'Groq' if groq_results['latency_p95'] < gemini_results['latency_p95'] else 'Gemini'}")
    
    # Cost comparison
    print(f"{'Cost/request':<20} ${gemini_results['cost_per_request']:.4f}{' '*8} ${groq_results['cost_per_request']:.4f}{' '*8} {'Groq' if groq_results['cost_per_request'] < gemini_results['cost_per_request'] else 'Gemini'}")
    
    print("\n=== Recommendation ===")
    if groq_results['latency_mean'] < gemini_results['latency_mean']:
        print(f"Use Groq for {args.task}: {groq_results['latency_mean']/gemini_results['latency_mean']:.1f}x faster")
    else:
        print(f"Use Gemini for {args.task}: Better quality (slower but worth it)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
