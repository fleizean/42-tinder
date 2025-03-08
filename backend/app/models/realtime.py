from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.db import Base


class NotificationType(enum.Enum):
    LIKE = "like"
    MATCH = "match"
    VISIT = "visit"
    MESSAGE = "message"
    UNMATCH = "unmatch"


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    sender_id = Column(String, ForeignKey("users.id"), nullable=True)
    type = Column(Enum(NotificationType))
    content = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    # Define relationships
    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    sender = relationship("User", foreign_keys=[sender_id])


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("users.id"))
    recipient_id = Column(String, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    # Define relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="messages_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="messages_received")


class Connection(Base):
    """
    Represents a connection between two users (when they like each other)
    This table helps track active connections for chat functionality
    """
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(String, ForeignKey("users.id"))
    user2_id = Column(String, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationships
    user1 = relationship("User", foreign_keys=[user1_id], backref="connections_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], backref="connections_as_user2")