"""WebSocket connection manager for real-time device communication."""

import json
import structlog
from typing import Dict
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per device."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        logger.info("ws_connected", device_id=device_id, total=len(self.active_connections))

    def disconnect(self, device_id: str):
        self.active_connections.pop(device_id, None)
        logger.info("ws_disconnected", device_id=device_id)

    async def send_message(self, device_id: str, message: str):
        ws = self.active_connections.get(device_id)
        if ws:
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.error("ws_send_failed", device_id=device_id, error=str(e))
                self.disconnect(device_id)

    async def broadcast(self, message: str):
        disconnected = []
        for device_id, ws in self.active_connections.items():
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(device_id)
        for d in disconnected:
            self.disconnect(d)
