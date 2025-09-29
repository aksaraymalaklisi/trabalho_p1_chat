from __future__ import annotations
from typing import Dict, Set
from fastapi import WebSocket


class WSManager:
    """Simple WebSocket room manager.

    Responsibilities:
    - track active connections per room
    - accept and disconnect sockets
    - broadcast messages safely
    """

    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    def disconnect(self, room: str, ws: WebSocket):
        conns = self.rooms.get(room)
        if conns and ws in conns:
            conns.remove(ws)
            if not conns:
                self.rooms.pop(room, None)

    async def broadcast(self, room: str, payload: dict):
        """Broadcast payload to all sockets in room. Remove dead sockets."""
        for ws in list(self.rooms.get(room, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(room, ws)
