"""
Event Bus — Pub/Sub system for agent coordination.
"""

import asyncio
from typing import Callable, Any
from collections import defaultdict


class EventBus:
    """Simple pub/sub event bus for agent coordination."""
    
    def __init__(self):
        self.subscribers: dict[str, list[Callable]] = defaultdict(list)
        self.event_history: list[dict] = []
    
    async def emit(self, event_type: str, data: dict):
        """Emit an event to all subscribers."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.event_history.append(event)
        
        # Keep only last 1000 events
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
        
        # Notify subscribers
        for handler in self.subscribers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                print(f"Event handler error: {e}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type."""
        self.subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
    
    def get_history(self, event_type: str = None, limit: int = 100) -> list:
        """Get event history, optionally filtered by type."""
        events = self.event_history
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[-limit:]
