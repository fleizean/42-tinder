from pydantic import BaseModel, EmailStr, validator
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

    def password_special_characters(cls, v):
        special_characters = "!@#$%^&*()-+.,"
        if not any(char in special_characters for char in v):
            raise ValueError('Şifre en az bir özel karakter içermelidir')
        return v
    
    def password_uppercase(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        return v

    def password_lowercase(cls, v):
        if not any(char.islower() for char in v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        return v
    
    def password_common_words(cls, v):
        common_words = [
            'password', '123456', '12345678', '1234', 'qwerty', '12345', 'abc123',
            'password1', 'admin', 'letmein', 'welcome', 'monkey', 'football', 'iloveyou'
        ]
        
        # Karakter değişim tablosu
        substitutions = {
            'a': ['@', '4', 'α'],
            'b': ['8', '6', 'ß'],
            'e': ['3', '€'],
            'i': ['1', '!', '|'],
            'l': ['1', '|', '!'],
            'o': ['0', 'ø', 'Ø'],
            's': ['$', '5'],
            't': ['7', '+'],
            'z': ['2']
        }
        
        # Şifrenin olası "orijinal" versiyonlarını oluşturma
        normalized_password = v.lower()
        
        # Karakter değişikliklerini tespit et ve normalize et
        for char, replacements in substitutions.items():
            for replacement in replacements:
                normalized_password = normalized_password.replace(replacement, char)
        
        # Sayıları kaldırma (sondan)
        cleaned_password = normalized_password.rstrip('0123456789')
        
        # Yaygın kelimelerin herhangi biri şifrenin bir parçası mı kontrol et
        for word in common_words:
            # Tam eşleşme
            if normalized_password == word:
                raise ValueError('Şifre çok yaygın bir şifre olamaz')
            
            # Basit karakter değişimiyle eşleşme
            if cleaned_password and cleaned_password == word:
                raise ValueError('Şifre yaygın bir şifrenin basit değişimi olamaz')
            
            # Şifre yaygın bir kelimeyi içeriyor mu
            if len(normalized_password) > 3 and word in normalized_password:
                raise ValueError('Şifre yaygın bir şifre içeremez')
        
        # Minimum şifre uzunluğunu kontrol et
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter uzunluğunda olmalıdır')
        
        # Şifre karmaşıklığını kontrol et
        has_upper = any(char.isupper() for char in v)
        has_lower = any(char.islower() for char in v)
        has_digit = any(char.isdigit() for char in v)
        has_special = any(not char.isalnum() for char in v)
        
        complexity_score = sum([has_upper, has_lower, has_digit, has_special])
        if complexity_score < 3:
            raise ValueError('Şifre en az 3 farklı karakter tipi içermelidir (büyük harf, küçük harf, rakam, özel karakter)')
        
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


# Token pair schema with refresh token
class TokenPair(Token):
    refresh_token: str


# Refresh token schema
class RefreshToken(BaseModel):
    refresh_token: str


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