"""
Analyze Costs Script

PURPOSE:
    Analyzes LLM and infrastructure costs from logs.
    Provides cost breakdown and optimization recommendations.

WHY COST ANALYSIS:
    No analysis: Budget overruns, waste
    Manual analysis: Time-consuming, error-prone
    Automated (this): Fast, accurate, actionable
    
    IMPACT: Cost savings, better budgeting

USAGE:
    python scripts/analyze_costs.py --period 30days
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_llm_costs(log_dir: str = 'logs/llm') -> dict:
    """
    Analyze LLM costs from logs
    
    WHY ANALYZE COSTS:
        - Identify expensive operations
        - Optimize prompt lengths
        - Choose cheaper LLMs
        - Budget forecasting
    
    Args:
        log_dir: Directory with LLM logs
        
    Returns:
        Cost analysis
    """
    costs_by_provider = defaultdict(float)
    tokens_by_provider = defaultdict(int)
    calls_by_provider = defaultdict(int)
    
    # Parse logs (placeholder - would read actual log files)
    # For demo, using sample data
    costs_by_provider['gemini'] = 10.50
    costs_by_provider['groq'] = 2.30
    tokens_by_provider['gemini'] = 500000
    tokens_by_provider['groq'] = 300000
    calls_by_provider['gemini'] = 1000
    calls_by_provider['groq'] = 1500
    
    total_cost = sum(costs_by_provider.values())
    total_tokens = sum(tokens_by_provider.values())
    total_calls = sum(calls_by_provider.values())
    
    return {
        'total_cost': total_cost,
        'total_tokens': total_tokens,
        'total_calls': total_calls,
        'by_provider': {
            provider: {
                'cost': costs_by_provider[provider],
                'tokens': tokens_by_provider[provider],
                'calls': calls_by_provider[provider],
                'cost_per_call': costs_by_provider[provider] / calls_by_provider[provider],
                'cost_per_1k_tokens': (costs_by_provider[provider] / tokens_by_provider[provider]) * 1000
            }
            for provider in costs_by_provider
        }
    }


def print_cost_analysis(analysis: dict):
    """Print cost analysis report"""
    print("\n=== Cost Analysis Report ===\n")
    
    print(f"Total Cost: ${analysis['total_cost']:.2f}")
    print(f"Total Tokens: {analysis['total_tokens']:,}")
    print(f"Total Calls: {analysis['total_calls']:,}")
    print(f"Average Cost/Call: ${analysis['total_cost']/analysis['total_calls']:.4f}")
    
    print("\n=== By Provider ===\n")
    for provider, stats in analysis['by_provider'].items():
        print(f"{provider.upper()}:")
        print(f"  Cost: ${stats['cost']:.2f} ({stats['cost']/analysis['total_cost']*100:.1f}%)")
        print(f"  Tokens: {stats['tokens']:,}")
        print(f"  Calls: {stats['calls']:,}")
        print(f"  Cost/Call: ${stats['cost_per_call']:.4f}")
        print(f"  Cost/1K tokens: ${stats['cost_per_1k_tokens']:.4f}")
        print()
    
    print("=== Recommendations ===")
    # Find cheapest provider
    cheapest = min(analysis['by_provider'].items(), key=lambda x: x[1]['cost_per_call'])
    print(f"✓ Use {cheapest[0]} for cost optimization (${cheapest[1]['cost_per_call']:.4f}/call)")
    print(f"✓ Potential savings: ${analysis['total_cost'] - (analysis['total_calls'] * cheapest[1]['cost_per_call']):.2f}")


def main():
    parser = argparse.ArgumentParser(description='Analyze costs')
    parser.add_argument('--period', default='30days', help='Analysis period')
    
    args = parser.parse_args()
    
    print(f"Analyzing costs for period: {args.period}")
    
    analysis = analyze_llm_costs()
    print_cost_analysis(analysis)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
