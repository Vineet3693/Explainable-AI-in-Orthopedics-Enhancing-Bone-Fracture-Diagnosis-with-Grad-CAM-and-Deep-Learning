"""
Retry Logic for Robust API Calls

PURPOSE:
    Provides decorators for retrying failed API calls with exponential backoff.
    Crucial for handling transient network errors and rate limits.

WHY RETRY LOGIC:
    LLM APIs are prone to rate limits and timeouts.
    Failing immediately leads to poor user experience.

USAGE:
    @with_retry(max_retries=3, base_delay=1.0)
    def call_api(): ...
"""

import time
import random
import logging
import functools
from typing import Type, Tuple, Callable

logger = logging.getLogger(__name__)


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for exponential backoff retry

    Args:
        max_retries: Maximum number of retries
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}")
                        raise e
                    
                    # Exponential backoff with jitter
                    # WHY JITTER: Prevents thundering herd problem
                    delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    jitter = random.uniform(0, 0.1 * delay)
                    total_delay = delay + jitter
                    
                    logger.warning(
                        f"Attempt {retries}/{max_retries} failed for {func.__name__} ({e}). "
                        f"Retrying in {total_delay:.2f}s..."
                    )
                    time.sleep(total_delay)
        return wrapper
    return decorator


__all__ = ['with_retry']
