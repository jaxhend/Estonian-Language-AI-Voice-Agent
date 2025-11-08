import asyncio
from collections import defaultdict
from typing import Callable, Any, Optional

class MemoryEventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, topic: str, callback: Optional[Callable] = None):
        """
        Subscribe to a topic. Can be used as a decorator or direct function call.

        Usage:
            @bus.subscribe("topic")
            def handler(event):
                ...

        Or:
            bus.subscribe("topic", handler)
        """
        if callback is not None:
            # Direct function call syntax
            self.subscribers[topic].append(callback)
            return callback
        else:
            # Decorator syntax
            def decorator(cb: Callable):
                self.subscribers[topic].append(cb)
                return cb
            return decorator

    def unsubscribe(self, topic: str, callback: Callable):
        """Remove a callback from a topic's subscribers."""
        if callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)

    async def publish(self, topic: str, event: Any):
        for callback in self.subscribers[topic]:
            await callback(event)

