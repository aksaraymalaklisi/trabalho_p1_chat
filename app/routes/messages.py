from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import Optional
from bson import ObjectId
from datetime import datetime, timezone

from ..config import DEFAULT_LIMIT, MAX_LIMIT
from ..database import get_db, insert_message
from ..models import MessageIn, serialize

router = APIRouter()


@router.get("/rooms/{room}/messages")
async def get_messages(room: str, limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT), before_id: Optional[str] = Query(None)):
    """Return messages for a room. If before_id is provided it must be a valid ObjectId or a 400 is returned."""
    query = {"room": room}
    if before_id:
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="before_id inválido")

    cursor = get_db()["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize(d) async for d in cursor]
    docs.reverse()
    next_cursor = docs[0]["_id"] if docs else None
    return {"items": docs, "next_cursor": next_cursor}


@router.post("/rooms/{room}/messages", status_code=201)
async def post_message(room: str, payload: MessageIn):
    """Validate message and save to DB. Empty content is rejected by Pydantic."""
    doc = {
        "room": room,
        "username": payload.username[:50],
        "content": payload.content[:1000],
        "created_at": datetime.now(timezone.utc),
    }
    inserted_id = await insert_message(doc)
    doc["_id"] = inserted_id
    return serialize(doc)
