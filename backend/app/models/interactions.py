from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base


class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    liker_id = Column(String, ForeignKey("profiles.id"))
    liked_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Define relationships
    liker = relationship("Profile", foreign_keys=[liker_id], backref="likes_given")
    liked = relationship("Profile", foreign_keys=[liked_id], backref="likes_received")


class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(String, ForeignKey("profiles.id"))
    visited_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Define relationships
    visitor = relationship("Profile", foreign_keys=[visitor_id], backref="visits_made")
    visited = relationship("Profile", foreign_keys=[visited_id], backref="visits_received")


class Block(Base):
    __tablename__ = "blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(String, ForeignKey("profiles.id"))
    blocked_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Define relationships
    blocker = relationship("Profile", foreign_keys=[blocker_id], backref="blocks_made")
    blocked = relationship("Profile", foreign_keys=[blocked_id], backref="blocks_received")


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(String, ForeignKey("profiles.id"))
    reported_id = Column(String, ForeignKey("profiles.id"))
    reason = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Define relationships
    reporter = relationship("Profile", foreign_keys=[reporter_id], backref="reports_made")
    reported = relationship("Profile", foreign_keys=[reported_id], backref="reports_received")