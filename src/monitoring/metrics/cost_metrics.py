"""
Cost Metrics for Tracking LLM and Infrastructure Costs

PURPOSE:
    Tracks all costs including LLM API calls, infrastructure, and storage.
    Essential for budget management and cost optimization.

WHY COST METRICS:
    No tracking: Budget overruns
    Manual tracking: Error-prone, delayed
    Automated metrics (this): Real-time cost visibility
    
    IMPACT: Prevent budget overruns, optimize spending

KEY METRICS:
    - llm_costs_total: Total LLM API costs
    - infrastructure_costs: Server/GPU costs
    - cost_per_diagnosis: Average cost per diagnosis
    - monthly_burn_rate: Current spending rate

USAGE:
    from src.monitoring.metrics.cost_metrics import CostMetrics
    
    metrics = CostMetrics()
    metrics.record_llm_cost(provider='gemini', tokens=1000, cost=0.002)
"""

from prometheus_client import Counter, Gauge
import logging

logger = logging.getLogger(__name__)


class CostMetrics:
    """Cost tracking metrics"""
    
    def __init__(self):
        self.llm_costs_total = Counter(
            'llm_costs_usd_total',
            'Total LLM API costs in USD',
            ['provider', 'model']
        )
        
        self.llm_tokens_total = Counter(
            'llm_tokens_total',
            'Total LLM tokens used',
            ['provider', 'model']
        )
        
        self.cost_per_diagnosis = Gauge(
            'cost_per_diagnosis_usd',
            'Average cost per diagnosis in USD'
        )
        
        self.monthly_burn_rate = Gauge(
            'monthly_burn_rate_usd',
            'Estimated monthly cost burn rate'
        )
    
    def record_llm_cost(
        self,
        provider: str,
        model: str,
        tokens: int,
        cost: float
    ):
        """Record LLM API cost"""
        self.llm_costs_total.labels(
            provider=provider,
            model=model
        ).inc(cost)
        
        self.llm_tokens_total.labels(
            provider=provider,
            model=model
        ).inc(tokens)
        
        logger.debug(f"LLM cost: ${cost:.4f} ({tokens} tokens, {provider}/{model})")


__all__ = ['CostMetrics']
