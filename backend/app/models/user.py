from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_password_token = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Last online status (for real-time features)
    is_online = Column(Boolean, default=False)
    last_online = Column(DateTime, nullable=True)
    
    # Location data (fallback if profile location is not set)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)