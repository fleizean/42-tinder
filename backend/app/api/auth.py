from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any

from app.core.db import get_db
from app.core.security import create_access_token, create_refresh_token, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, TokenPair, RefreshToken, PasswordReset, PasswordChange
from app.services.auth import (
    authenticate_user, create_user, verify_user, request_password_reset,
    reset_password, change_password, update_last_activity, update_refresh_token,
    validate_refresh_token, invalidate_refresh_token
)

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user
    """
    # Check if username already exists
    result = await db.execute(select(User).filter(User.username == user_data.username))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten kayıtlı"
        )
    
    # Check if email already exists
    result = await db.execute(select(User).filter(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı"
        )
    
    # Create user
    await create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    return {
        "message": "User registered successfully. Please check your email to verify your account."
    }


@router.post("/login", response_model=TokenPair)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification instructions.",
        )
    
    # Generate access token
    access_token = create_access_token(user.id)
    
    # Generate refresh token
    refresh_token = create_refresh_token(user.id)
    
    # Store refresh token in the database
    await update_refresh_token(db, user.id, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login/json", response_model=TokenPair)
async def login_json(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    JSON compatible login (alternative to OAuth2)
    """
    user = await authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email onaylanmamış. Lütfen emailinizi kontrol edin.",
        )
    
    # Generate access token
    access_token = create_access_token(user.id)
    
    # Generate refresh token
    refresh_token = create_refresh_token(user.id)
    
    # Store refresh token in the database
    await update_refresh_token(db, user.id, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenPair)
async def refresh_token_endpoint(
    refresh_token_data: RefreshToken,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    # Validate refresh token
    user = await validate_refresh_token(db, refresh_token_data.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Generate new access token
    access_token = create_access_token(user.id)
    
    # Generate new refresh token (rotating refresh tokens for better security)
    new_refresh_token = create_refresh_token(user.id)
    
    # Update refresh token in database
    await update_refresh_token(db, user.id, new_refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/verify", response_model=dict)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Verify email with token
    """
    user = await verify_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz veya süresi dolmuş onay kodu"
        )
    
    return {
        "message": "Başarıyla onaylandı. Artık giriş yapabilirsiniz."
    }


@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Request password reset
    """
    # Process in background to prevent timing attacks
    background_tasks.add_task(request_password_reset, db, email)
    
    return {
        "message": "If your email is registered, you will receive password reset instructions."
    }


@router.post("/reset-password", response_model=dict)
async def reset_password_route(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Reset password with token
    """
    user = await reset_password(db, reset_data.token, reset_data.new_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {
        "message": "Password reset successfully. You can now log in with your new password."
    }


@router.post("/change-password", response_model=dict)
async def change_password_route(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Change password
    """
    user = await change_password(
        db, current_user.id, password_data.current_password, password_data.new_password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    return {
        "message": "Password changed successfully"
    }


@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Logout (invalidate refresh token and update online status)
    """
    await update_last_activity(db, current_user.id, is_online=False)
    await invalidate_refresh_token(db, current_user.id)
    
    return {
        "message": "Logged out successfully"
    }