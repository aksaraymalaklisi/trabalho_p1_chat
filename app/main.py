from __future__ import annotations
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import DEFAULT_LIMIT
from .ws_manager import WSManager
from .models import serialize
from .database import get_db
from .routes import messages as messages_router

app = FastAPI(title="FastAPI Chat + MongoDB Atlas")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("app/static/index.html")

# include routes
app.include_router(messages_router.router)

# websocket manager
manager = WSManager()

@app.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    """WebSocket endpoint for a room. Sends initial history and broadcasts incoming messages.

    Messages received over WS are validated minimally and empty messages are ignored.
    """
    await manager.connect(room, ws)
    try:
        cursor = get_db()["messages"].find({"room": room}).sort("_id", -1).limit(DEFAULT_LIMIT)
        items = [serialize(d) async for d in cursor]
        items.reverse()
        await ws.send_json({"type": "history", "items": items})

        while True:
            payload = await ws.receive_json()
            username = str(payload.get("username", "anon"))[:50].strip()
            content = str(payload.get("content", "")).strip()
            if not content:
                # ignore empty messages
                continue
            doc = {
                "room": room,
                "username": username,
                "content": content,
                "created_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
            }
            res = await get_db()["messages"].insert_one(doc)
            doc["_id"] = res.inserted_id
            await manager.broadcast(room, {"type": "message", "item": serialize(doc)})
    except WebSocketDisconnect:
        manager.disconnect(room, ws)
