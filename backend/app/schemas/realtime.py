from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.realtime import NotificationType


# Message schemas
class MessageCreate(BaseModel):
    recipient_id: str
    content: str


class Message(BaseModel):
    id: int
    sender_id: str
    recipient_id: str
    content: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Notification schemas
class Notification(BaseModel):
    id: int
    user_id: str
    sender_id: Optional[str] = None
    type: NotificationType
    content: Optional[str] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Connection schemas
class Connection(BaseModel):
    id: int
    user1_id: str
    user2_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str  # "message", "notification", "online_status", etc.
    data: dict