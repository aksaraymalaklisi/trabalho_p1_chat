from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone

class MessageIn(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=1000)

    @field_validator("username", mode="before")
    def strip_username(cls, v):
        return str(v).strip()

    @field_validator("content", mode="before")
    def strip_content(cls, v):
        return str(v).strip()

class MessageOut(BaseModel):
    # Use plain string for `id` (alias `_id`) to avoid depending on pydantic
    # internals for ObjectId conversion. The DB layer/serialize helper
    # ensures `_id` is represented as string.
    id: str = Field(..., alias="_id")
    room: str
    username: str
    content: str
    created_at: datetime

    model_config = {
        "populate_by_name": True,
    }
    
def serialize(doc: dict) -> dict:
    """Serialize a MongoDB document into JSON-friendly dict."""
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    if "created_at" in d and isinstance(d["created_at"], datetime):
        if d["created_at"].tzinfo is None:
            d["created_at"] = d["created_at"].replace(tzinfo=timezone.utc).isoformat()
        else:
            d["created_at"] = d["created_at"].isoformat()
    return d
