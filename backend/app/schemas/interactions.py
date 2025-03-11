from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Like schemas
class LikeCreate(BaseModel):
    liked_id: str


class Like(BaseModel):
    id: int
    liker_id: str
    liked_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Visit schemas
class Visit(BaseModel):
    id: int
    visitor_id: str
    visited_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Block schemas
class BlockCreate(BaseModel):
    blocked_id: str
    
    
class Block(BaseModel):
    id: int
    blocker_id: str
    blocked_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Report schemas
class ReportCreate(BaseModel):
    reported_id: str
    reason: str
    description: Optional[str] = None


class Report(BaseModel):
    id: int
    reporter_id: str
    reported_id: str
    reason: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True