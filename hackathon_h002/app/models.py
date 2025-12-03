from pydantic import BaseModel
from typing import Optional, Dict


class Location(BaseModel):
    lat: float
    lon: float


class ChatRequest(BaseModel):
    user_id: str
    message: str
    location: Optional[Dict] = None  # {"lat": ..., "lon": ...}


class ChatResponse(BaseModel):
    reply: str
    used_store: Optional[str] = None
    debug_context: Optional[Dict] = None
