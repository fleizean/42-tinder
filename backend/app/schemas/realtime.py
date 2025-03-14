from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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
        from_attributes = True


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
        from_attributes = True


# Connection schemas
class Connection(BaseModel):
    id: int
    user1_id: str
    user2_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# User schema (simplified for use in conversations)
class UserInfo(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    is_online: bool
    last_online: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Conversation schema for returning in the API
class Conversation(BaseModel):
    connection: Connection
    user: UserInfo
    recent_message: Optional[Message] = None
    unread_count: int
    
    class Config:
        from_attributes = True


# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str  # "message", "notification", "online_status", etc.
    data: Dict[str, Any]