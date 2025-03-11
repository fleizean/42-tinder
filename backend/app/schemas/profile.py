from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime, timezone
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
        from_attributes = True


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
    backend_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Profile schemas
class ProfileBase(BaseModel):
    gender: Optional[Gender] = None
    sexual_preference: Optional[SexualPreference] = None
    biography: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    birth_date: Optional[datetime] = None



class ProfileCreate(ProfileBase):
    pass




class ProfileUpdate(ProfileBase):
    birth_date: Optional[datetime] = None

    @validator('birth_date')
    def validate_birth_date(cls, birth_date):
        if birth_date:
            # Convert to UTC timezone if naive
            if birth_date.tzinfo is None:
                birth_date = birth_date.replace(tzinfo=timezone.utc)
            
            today = datetime.now(timezone.utc)
            
            # Check if date is in future
            if birth_date > today:
                raise ValueError("Doğum tarihi bugünden büyük olamaz")
            
            # Check minimum age (16)
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 16:
                raise ValueError("Platform kullanımı için minimum yaş sınırı 16'dır")
            
            # Check reasonable date range
            if birth_date.year < 1900:
                raise ValueError("Geçerli bir doğum tarihi girin")
            
            # Check maximum age (70)
            if age > 70:
                raise ValueError("Geçerli bir doğum tarihi girin")
            
        return birth_date


class ProfileTagUpdate(BaseModel):
    tags: List[str]

class TagUpdateSchema(BaseModel):
    tags: List[str] = Field(
        default=[],
        description="List of tags for the profile"
    )

    @validator('tags')
    def validate_tags(cls, tags):
        BLACKLISTED_TAGS = [
            'admin', 'moderator', 'staff', 'support',
            'system', 'crushit', 'crushitapp'
        ]
        
        for tag in tags:
            # Check length
            if len(tag) < 2 or len(tag) > 20:
                raise ValueError("Etiket adı 2 ila 20 karakter arasında olmalıdır")
                
            # Check characters - only allow letters, numbers, and hyphens
            if not tag.replace('-', '').isalnum():
                raise ValueError("Etiket sadece harf ve rakam içerebilir (özel karakterler kullanılamaz)")
            
            # Check for valid hyphen usage
            if tag.startswith('-') or tag.endswith('-'):
                raise ValueError("Etiket tire (-) ile başlayamaz veya bitemez")
            
            # Check for consecutive hyphens
            if '--' in tag:
                raise ValueError("Etiket ardışık tire (-) içeremez")
            
            # Check for special characters
            allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-')
            if not all(c in allowed_chars for c in tag):
                raise ValueError("Etiket sadece İngilizce harf, rakam ve tire (-) içerebilir")
                
            # Check blacklist
            if tag.lower() in BLACKLISTED_TAGS:
                raise ValueError(f"'{tag}' etiketi kullanılamaz")
                
            # Check if tag contains only hyphens
            if all(c == '-' for c in tag):
                raise ValueError("Etiket sadece tire (-) karakterinden oluşamaz")
                
        return tags


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
        from_attributes = True


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
    fame_rating: float = 0.0
    is_online: bool
    last_online: Optional[datetime] = None
    pictures: List[ProfilePicture] = []
    tags: List[Tag] = []
    birth_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Location update schema
class LocationUpdate(BaseModel):
    latitude: float
    longitude: float