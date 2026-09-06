"""
Netra — WebSocket Manager
Manages real-time WebSocket connections, channel subscriptions, and event broadcasting.
"""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any, Optional
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect


class WebSocketManager:
    """Manages WebSocket connections and channel-based message routing."""

    CHANNELS = [
        "telemetry", "topology", "alerts", "incidents",
        "forecast", "risk", "health", "deception",
        "replay", "dashboard",
    ]

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._subscriptions: dict[str, set[str]] = defaultdict(set)
        self._channel_subscribers: dict[str, set[str]] = defaultdict(set)
        self._connection_count: int = 0
        self._total_messages_sent: int = 0

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        await websocket.accept()
        if not client_id:
            self._connection_count += 1
            client_id = f"client_{self._connection_count}_{int(time.time())}"
        self._connections[client_id] = websocket
        for channel in self.CHANNELS:
            self._subscriptions[client_id].add(channel)
            self._channel_subscribers[channel].add(client_id)
        return client_id

    def disconnect(self, client_id: str) -> None:
        self._connections.pop(client_id, None)
        channels = self._subscriptions.pop(client_id, set())
        for channel in channels:
            self._channel_subscribers[channel].discard(client_id)

    async def subscribe(self, client_id: str, channels: list[str]) -> None:
        for ch in channels:
            if ch in self.CHANNELS:
                self._subscriptions[client_id].add(ch)
                self._channel_subscribers[ch].add(client_id)

    async def unsubscribe(self, client_id: str, channels: list[str]) -> None:
        for ch in channels:
            self._subscriptions[client_id].discard(ch)
            self._channel_subscribers[ch].discard(client_id)

    async def broadcast_to_channel(self, channel: str, event: str, data: Any) -> int:
        message = json.dumps({
            "channel": channel,
            "event": event,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, default=str)
        subscribers = self._channel_subscribers.get(channel, set())
        sent = 0
        disconnected = []
        for client_id in subscribers:
            ws = self._connections.get(client_id)
            if ws:
                try:
                    await ws.send_text(message)
                    sent += 1
                    self._total_messages_sent += 1
                except Exception:
                    disconnected.append(client_id)
        for cid in disconnected:
            self.disconnect(cid)
        return sent

    async def send_to_client(self, client_id: str, channel: str, event: str, data: Any) -> bool:
        ws = self._connections.get(client_id)
        if not ws:
            return False
        message = json.dumps({
            "channel": channel,
            "event": event,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, default=str)
        try:
            await ws.send_text(message)
            self._total_messages_sent += 1
            return True
        except Exception:
            self.disconnect(client_id)
            return False

    async def broadcast_all(self, event: str, data: Any) -> int:
        total = 0
        for channel in self.CHANNELS:
            total += await self.broadcast_to_channel(channel, event, data)
        return total

    def get_stats(self) -> dict[str, Any]:
        return {
            "active_connections": len(self._connections),
            "total_messages_sent": self._total_messages_sent,
            "channel_subscribers": {ch: len(subs) for ch, subs in self._channel_subscribers.items()},
        }

    async def handle_client_message(self, client_id: str, raw_message: str) -> None:
        try:
            msg = json.loads(raw_message)
        except json.JSONDecodeError:
            return
        action = msg.get("action")
        if action == "subscribe":
            channels = msg.get("channels", [])
            await self.subscribe(client_id, channels)
        elif action == "unsubscribe":
            channels = msg.get("channels", [])
            await self.unsubscribe(client_id, channels)
        elif action == "ping":
            await self.send_to_client(client_id, "health", "pong", {"status": "ok"})


ws_manager = WebSocketManager()
