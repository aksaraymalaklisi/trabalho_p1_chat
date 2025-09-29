from __future__ import annotations
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

from .config import MONGO_URL, MONGO_DB

_client: Optional[AsyncIOMotorClient] = None

def get_db():
    """Return a Motor database instance. Raises RuntimeError when MONGO_URL is not set.

    This function keeps a module-level client to reuse connections.
    """
    global _client
    if _client is None:
        if not MONGO_URL:
            raise RuntimeError("MONGO_URL não configurado. Veja .env")
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[MONGO_DB]

async def insert_message(doc: dict):
    """Insert a message document into the messages collection.

    Returns the inserted_id on success. Raises PyMongoError on failure.
    """
    db = get_db()
    res = await db["messages"].insert_one(doc)
    return res.inserted_id
