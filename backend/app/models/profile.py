from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, Table, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from app.core.db import Base


# Define enums for profile attributes
class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"


class SexualPreference(enum.Enum):
    HETEROSEXUAL = "heterosexual"
    HOMOSEXUAL = "homosexual"
    BISEXUAL = "bisexual"
    OTHER = "other"


# Association table for profile tags
profile_tags = Table(
    "profile_tags",
    Base.metadata,
    Column("profile_id", String, ForeignKey("profiles.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class ProfilePicture(Base):
    __tablename__ = "profile_pictures"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String, ForeignKey("profiles.id"))
    file_path = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    profile = relationship("Profile", back_populates="pictures")


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    
    # Personal information
    gender = Column(Enum(Gender), nullable=True)
    sexual_preference = Column(Enum(SexualPreference), nullable=True)
    biography = Column(Text, nullable=True)
    
    # Location information
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Fame rating (calculated based on likes, views, etc.)
    fame_rating = Column(Float, default=0.0)
    
    # Profile completion status
    is_complete = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    pictures = relationship("ProfilePicture", back_populates="profile", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=profile_tags, backref="profiles")

    birth_date = Column(DateTime(timezone=True), nullable=True)
    
    # Profile interactions (defined in respective models)
    # likes = relationship("Like", foreign_keys="Like.liker_id", back_populates="liker")
    # liked_by = relationship("Like", foreign_keys="Like.liked_id", back_populates="liked")
    # visits = relationship("Visit", foreign_keys="Visit.visitor_id", back_populates="visitor")
    # visited_by = relationship("Visit", foreign_keys="Visit.visited_id", back_populates="visited")
    # blocks = relationship("Block", foreign_keys="Block.blocker_id", back_populates="blocker")
    # blocked_by = relationship("Block", foreign_keys="Block.blocked_id", back_populates="blocked")
    # reports = relationship("Report", foreign_keys="Report.reporter_id", back_populates="reporter")
    # reported_by = relationship("Report", foreign_keys="Report.reported_id", back_populates="reported")