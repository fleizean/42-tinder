from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

# Import gender and sexual preference enums from models
from app.models.profile import Gender, SexualPreference


# Tag schemas
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    
    class Config:
        orm_mode = True


# Profile picture schemas
class ProfilePictureBase(BaseModel):
    is_primary: bool = False


class ProfilePictureCreate(ProfilePictureBase):
    # File will be handled separately
    pass


class ProfilePicture(ProfilePictureBase):
    id: int
    profile_id: str
    file_path: str
    created_at: datetime
    
    class Config:
        orm_mode = True


# Profile schemas
class ProfileBase(BaseModel):
    gender: Optional[Gender] = None
    sexual_preference: Optional[SexualPreference] = None
    biography: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileTagUpdate(BaseModel):
    tags: List[str]


class Profile(ProfileBase):
    id: str
    user_id: str
    fame_rating: float
    is_complete: bool
    created_at: datetime
    updated_at: datetime
    pictures: List[ProfilePicture] = []
    tags: List[Tag] = []
    
    class Config:
        orm_mode = True


# Public profile schema (for other users to view)
class PublicProfile(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    gender: Optional[Gender] = None
    sexual_preference: Optional[SexualPreference] = None
    biography: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fame_rating: float
    is_online: bool
    last_online: Optional[datetime] = None
    pictures: List[ProfilePicture] = []
    tags: List[Tag] = []
    
    class Config:
        orm_mode = True


# Location update schema
class LocationUpdate(BaseModel):
    latitude: float
    longitude: float