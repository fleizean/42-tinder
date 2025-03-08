from datetime import datetime, timedelta
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.profile import Profile
from app.services.email import send_verification_email, send_password_reset_email


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password
    """
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update online status
    user.is_online = True
    user.last_login = datetime.utcnow()
    db.add(user)
    await db.commit()
    
    return user


async def create_user(db: AsyncSession, username: str, email: str, password: str, first_name: str, last_name: str) -> User:
    """
    Create a new user
    """
    # Generate verification token
    verification_token = str(uuid.uuid4())
    
    # Create the user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        hashed_password=get_password_hash(password),
        verification_token=verification_token,
        is_verified=False
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Initialize empty profile
    profile = Profile(
        id=str(uuid.uuid4()),
        user_id=user.id,
        is_complete=False
    )
    
    db.add(profile)
    await db.commit()
    
    # Send verification email
    await send_verification_email(email, username, verification_token)
    
    return user


async def verify_user(db: AsyncSession, verification_token: str) -> Optional[User]:
    """
    Verify a user's email with the verification token
    """
    result = await db.execute(select(User).filter(User.verification_token == verification_token))
    user = result.scalars().first()
    
    if not user:
        return None
    
    # Mark as verified and remove token
    user.is_verified = True
    user.verification_token = None
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def request_password_reset(db: AsyncSession, email: str) -> bool:
    """
    Request a password reset for a user
    """
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    
    if not user:
        # Return True anyway to prevent email enumeration
        return True
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    
    # Update user
    user.reset_password_token = reset_token
    db.add(user)
    await db.commit()
    
    # Send password reset email
    await send_password_reset_email(email, user.username, reset_token)
    
    return True


async def reset_password(db: AsyncSession, token: str, new_password: str) -> Optional[User]:
    """
    Reset a user's password with the reset token
    """
    result = await db.execute(select(User).filter(User.reset_password_token == token))
    user = result.scalars().first()
    
    if not user:
        return None
    
    # Update password and remove token
    user.hashed_password = get_password_hash(new_password)
    user.reset_password_token = None
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def change_password(db: AsyncSession, user_id: str, current_password: str, new_password: str) -> Optional[User]:
    """
    Change a user's password
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return None
    
    # Verify current password
    if not verify_password(current_password, user.hashed_password):
        return None
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def update_last_activity(db: AsyncSession, user_id: str, is_online: bool = True) -> Optional[User]:
    """
    Update user's last activity and online status
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return None
    
    # Update online status
    user.is_online = is_online
    if not is_online:
        user.last_online = datetime.utcnow()
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user