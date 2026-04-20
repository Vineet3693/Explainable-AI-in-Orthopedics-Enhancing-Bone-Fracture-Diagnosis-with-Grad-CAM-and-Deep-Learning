"""
LLM usage and cost tracking metrics

PURPOSE:
    Tracks LLM API usage, costs, and performance for both Gemini and Groq.
    Enables cost monitoring and optimization.

METRICS TRACKED:
    - API calls (total, by provider, by operation)
    - Token usage (input, output, total)
    - Cost (per call, cumulative)
    - Response time (mean, p95)
    - Error rate (by provider)

COST TRACKING:
    - Gemini Pro Vision: $0.002 per image
    - Gemini Pro: $0.0005 per 1k tokens
    - Groq: $0.0001 per 1k tokens

EXAMPLE USE:
    >>> from src.monitoring.metrics.llm_metrics import LLMMetrics
    >>> metrics = LLMMetrics()
    >>> metrics.record_llm_call('gemini', 'vision', tokens=500, cost=0.002, time_ms=2000)
"""

from prometheus_client import Counter, Histogram, Gauge
import logging

logger = logging.getLogger(__name__)

# LLM call counter
llm_calls = Counter(
    'llm_calls_total',
    'Total LLM API calls',
    ['provider', 'operation']
)

# Token usage counter
token_usage = Counter(
    'llm_tokens_total',
    'Total tokens used',
    ['provider', 'type']
)

# Cost counter
llm_cost = Counter(
    'llm_cost_dollars_total',
    'Total LLM cost in dollars',
    ['provider']
)

# Response time histogram
llm_response_time = Histogram(
    'llm_response_seconds',
    'LLM response time',
    ['provider'],
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)


class LLMMetrics:
    """Tracks LLM usage and costs"""
    
    def record_llm_call(self, provider: str, operation: str, tokens: int, cost: float, time_ms: float):
        """Record an LLM API call"""
        llm_calls.labels(provider=provider, operation=operation).inc()
        token_usage.labels(provider=provider, type='total').inc(tokens)
        llm_cost.labels(provider=provider).inc(cost)
        llm_response_time.labels(provider=provider).observe(time_ms / 1000)
