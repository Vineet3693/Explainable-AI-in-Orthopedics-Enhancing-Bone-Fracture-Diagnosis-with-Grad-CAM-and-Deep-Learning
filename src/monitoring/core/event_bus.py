"""
Event Bus for Monitoring Events

PURPOSE:
    Event-driven monitoring system for decoupled components.
    Allows components to publish/subscribe to monitoring events.

USAGE:
    from src.monitoring.core.event_bus import EventBus
    
    bus = EventBus()
    bus.subscribe('prediction_made', handler_function)
    bus.publish('prediction_made', data={'result': 'fracture'})
"""

import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)


class EventBus:
    """Event bus for monitoring events"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to event: {event_type}")
    
    def publish(self, event_type: str, data: Any = None):
        """Publish an event"""
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")


__all__ = ['EventBus']
