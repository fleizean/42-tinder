from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any

from app.core.db import get_db
from app.core.security import get_current_user, get_current_verified_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services.auth import update_last_activity

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update current user
    """
    # Check if username is being changed and if it's already taken
    if user_data.username and user_data.username != current_user.username:
        result = await db.execute(select(User).filter(User.username == user_data.username))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Check if email is being changed and if it's already taken
    if user_data.email and user_data.email != current_user.email:
        result = await db.execute(select(User).filter(User.email == user_data.email))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user attributes
    for key, value in user_data.dict(exclude_unset=True).items():
        if key != "password":  # Password handled separately
            setattr(current_user, key, value)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/heartbeat", response_model=dict)
async def user_heartbeat(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update user's last activity timestamp (for online status)
    """
    await update_last_activity(db, current_user.id, is_online=True)
    
    return {
        "status": "ok"
    }