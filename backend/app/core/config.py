from pydantic_settings import BaseSettings
from typing import List
from pydantic import EmailStr, AnyHttpUrl


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "CrushIt"
    API_V1_STR: str = "/api"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    BACKEND_URL: str = "http://localhost:8000"

    # Database settings
    DATABASE_URL: str
    
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    # SQLAdmin credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"

    FRONTEND_URL: str
    MEDIA_ROOT: str = "./media"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()