from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from unidecode import unidecode

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        # Convert Turkish characters to ASCII equivalents
        normalized = unidecode(v)
        
        # Check if contains only allowed characters
        if not normalized.isalnum():
            raise ValueError('Kullanıcı adı yalnızca harf ve rakamlardan oluşabilir')
            
        # Check if original had Turkish characters
        if v != normalized:
            raise ValueError('Kullanıcı adında Türkçe karakter kullanılamaz (ğ,ü,ş,i,ö,ç)')
            
        return normalized
    
    @validator('password')
    def password_min_length(cls, v):
        assert len(v) >= 8, 'Şifre en az 8 karakter olmalıdır'
        return v


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @validator('password')
    def password_min_length(cls, v):
        if v is not None:
            assert len(v) >= 8, 'Şifre en az 8 karakter olmalıdır'
        return v


# Properties to return via API
class User(UserBase):
    id: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    is_online: bool
    last_online: Optional[datetime] = None
    is_verified: bool
    
    class Config:
        from_attributes = True


# Properties for user authentication
class UserLogin(BaseModel):
    username: str
    password: str


# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str


# Token payload
class TokenPayload(BaseModel):
    sub: Optional[str] = None


# Password reset
class PasswordReset(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def password_min_length(cls, v):
        assert len(v) >= 8, 'Şifre en az 8 karakter olmalıdır'
        return v


# Password change
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def password_min_length(cls, v):
        assert len(v) >= 8, 'Şifre en az 8 karakter olmalıdır'
        return v