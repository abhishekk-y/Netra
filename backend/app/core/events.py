import json
import asyncio
from typing import Any, Callable, Dict, List
import structlog

logger = structlog.get_logger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    async def publish(self, channel: str, message: Any) -> None:
        logger.debug("Publishing event", channel=channel)
        if channel in self._subscribers:
            for callback in self._subscribers[channel]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error("Error in event subscriber", error=str(e), channel=channel)

    def subscribe(self, channel: str, callback: Callable) -> None:
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)
        logger.info("Subscribed to channel", channel=channel)

event_bus = EventBus()
