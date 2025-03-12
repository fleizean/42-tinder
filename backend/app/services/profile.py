from math import cos
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import selectinload
import uuid
import os
from datetime import datetime

from app.models.profile import Profile, Tag, ProfilePicture, Gender, SexualPreference, profile_tags
from app.models.user import User
from app.models.interactions import Like, Visit, Block, Report
from app.core.config import settings
from tkinter.tix import Select


async def get_profile_by_user_id(db: AsyncSession, user_id: str) -> Optional[Profile]:
    """
    Get a profile by user ID
    """
    result = await db.execute(
        select(Profile)
        .options(selectinload(Profile.pictures), selectinload(Profile.tags))
        .filter(Profile.user_id == user_id)
    )
    return result.scalars().first()

async def get_profile_by_username(db: AsyncSession, username: str) -> Optional[Profile]:
    """
    Get a profile by username
    """
    result = await db.execute(
        select(Profile)
        .options(selectinload(Profile.pictures), selectinload(Profile.tags))
        .join(User)
        .filter(User.username == username)
    )
    return result.scalars().first()


async def get_profile_by_id(db: AsyncSession, profile_id: str) -> Optional[Profile]:
    """
    Get a profile by profile ID
    """
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    return result.scalars().first()


async def update_profile(db: AsyncSession, profile_id: str, profile_data: Dict[str, Any]) -> Optional[Profile]:
    """
    Update a profile
    """
    result = await db.execute(
        select(Profile)
        .options(selectinload(Profile.pictures), selectinload(Profile.tags))
        .filter(Profile.id == profile_id)
    )
    profile = result.scalars().first()
    
    if not profile:
        return None
    
    # Update profile attributes
    for key, value in profile_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    # Check if profile is complete
    profile.is_complete = is_profile_complete(profile)
    
    # Update profile
    profile.updated_at = datetime.utcnow()
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return profile


def is_profile_complete(profile: Profile) -> bool:
    """
    Check if a profile is complete
    """
    # Define required fields
    required_fields = ['gender', 'sexual_preference', 'biography', 'latitude', 'longitude']
    
    # Check if all required fields are filled
    for field in required_fields:
        if not getattr(profile, field):
            return False
    
    # Check if profile has at least one picture
    if not profile.pictures or len(profile.pictures) == 0:
        return False
    
    # Check if profile has at least one tag
    if not profile.tags or len(profile.tags) == 0:
        return False
    
    return True


async def add_tag_to_profile(db: AsyncSession, profile_id: str, tag_name: str) -> Optional[Tag]:
    """
    Add a tag to a profile
    """
    # Get profile
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return None
    
    # Check if tag exists
    result = await db.execute(select(Tag).filter(func.lower(Tag.name) == func.lower(tag_name)))
    tag = result.scalars().first()
    
    # Create tag if it doesn't exist
    if not tag:
        tag = Tag(name=tag_name.lower())
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
    
    # Add tag to profile if not already added
    if tag not in profile.tags:
        profile.tags.append(tag)
        db.add(profile)
        await db.commit()
    
    return tag


async def remove_tag_from_profile(db: AsyncSession, profile_id: str, tag_id: int) -> bool:
    """
    Remove a tag from a profile
    """
    # Get profile
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return False
    
    # Get tag
    result = await db.execute(select(Tag).filter(Tag.id == tag_id))
    tag = result.scalars().first()
    
    if not tag:
        return False
    
    # Remove tag from profile
    if tag in profile.tags:
        profile.tags.remove(tag)
        db.add(profile)
        await db.commit()
    
    return True


async def update_profile_tags(db: AsyncSession, profile_id: str, tag_names: List[str]) -> List[Tag]:
    """
    Update a profile's tags (replace all tags)
    """
    # Get profile
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return []
    
    # Clear existing tags
    profile.tags = []
    
    # Add new tags
    tags = []
    for tag_name in tag_names:
        tag = await add_tag_to_profile(db, profile_id, tag_name)
        if tag:
            tags.append(tag)
    
    # Check if profile is complete
    profile.is_complete = is_profile_complete(profile)
    db.add(profile)
    await db.commit()
    
    return tags


async def add_profile_picture(db: AsyncSession, profile_id: str, file_path: str, backend_url: str, is_primary: bool = False) -> Optional[ProfilePicture]:
    """
    Add a profile picture
    """
    # Get profile
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return None
    
    # Count existing pictures
    result = await db.execute(select(func.count()).select_from(ProfilePicture).filter(ProfilePicture.profile_id == profile_id))
    count = result.scalar()
    
    # Check if maximum pictures reached
    if count >= 5:
        return None
    
    # If this is the first picture or is_primary is True, set as primary
    if count == 0 or is_primary:
        # If setting as primary, unset any existing primary pictures
        if is_primary:
            result = await db.execute(select(ProfilePicture).filter(ProfilePicture.profile_id == profile_id))
            pictures = result.scalars().all()
            
            for pic in pictures:
                pic.is_primary = False
                db.add(pic)
        
        is_primary = True
    
    # Create profile picture
    picture = ProfilePicture(
        profile_id=profile_id,
        file_path=file_path,
        backend_url=backend_url,
        is_primary=is_primary
    )
    
    db.add(picture)
    await db.commit()
    await db.refresh(picture)
    
    # Check if profile is complete
    profile.is_complete = is_profile_complete(profile)
    db.add(profile)
    await db.commit()
    
    return picture


async def remove_profile_picture(db: AsyncSession, profile_id: str, picture_id: int) -> bool:
    """
    Remove a profile picture
    """
    # Get profile
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return False
    
    # Get picture
    result = await db.execute(select(ProfilePicture).filter(
        ProfilePicture.id == picture_id,
        ProfilePicture.profile_id == profile_id
    ))
    picture = result.scalars().first()
    
    if not picture:
        return False
    
    # Check if this is the primary picture
    was_primary = picture.is_primary
    
    # Remove picture from filesystem
    if os.path.exists(picture.file_path):
        os.remove(picture.file_path)
    
    # Remove picture from database
    await db.delete(picture)
    await db.commit()
    
    # If this was the primary picture, set another picture as primary
    if was_primary:
        # Get all remaining pictures
        result = await db.execute(select(ProfilePicture).filter(ProfilePicture.profile_id == profile_id))
        pictures = result.scalars().all()
        
        if pictures:
            # Set first picture as primary
            pictures[0].is_primary = True
            db.add(pictures[0])
            await db.commit()
    
    # Check if profile is complete
    profile.is_complete = is_profile_complete(profile)
    db.add(profile)
    await db.commit()
    
    return True


async def set_primary_picture(db: AsyncSession, profile_id: str, picture_id: int) -> bool:
    """
    Set a profile picture as primary
    """
    # Get profile
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return False
    
    # Get picture
    result = await db.execute(select(ProfilePicture).filter(
        ProfilePicture.id == picture_id,
        ProfilePicture.profile_id == profile_id
    ))
    picture = result.scalars().first()
    
    if not picture:
        return False
    
    # Get all profile pictures
    result = await db.execute(select(ProfilePicture).filter(ProfilePicture.profile_id == profile_id))
    pictures = result.scalars().all()
    
    # Unset primary for all pictures
    for pic in pictures:
        pic.is_primary = (pic.id == picture_id)
        db.add(pic)
    
    await db.commit()
    
    return True


async def update_fame_rating(db: AsyncSession, profile_id: str) -> float:
    """
    Update a profile's fame rating based on likes, visits, etc.
    """
    # Get profile
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    profile = result.scalars().first()
    
    if not profile:
        return 0.0
    
    # Count likes
    result = await db.execute(select(func.count()).select_from(Like).filter(Like.liked_id == profile_id))
    likes_count = result.scalar()
    
    # Count visits
    result = await db.execute(select(func.count()).select_from(Visit).filter(Visit.visited_id == profile_id))
    visits_count = result.scalar()
    
    # Get total user count for normalization
    result = await db.execute(select(func.count()).select_from(User))
    total_users = result.scalar()
    
    # Calculate fame rating (algorithm can be adjusted)
    if total_users > 0:
        # Formula: (likes * 2 + visits) / total_users * 10
        # This gives a rating between 0 and ~10, where 10 is very famous
        fame_rating = (likes_count * 2 + visits_count) / total_users * 10
        fame_rating = min(10.0, fame_rating)  # Cap at 10
    else:
        fame_rating = 0.0
    
    # Update profile
    profile.fame_rating = fame_rating
    db.add(profile)
    await db.commit()
    
    return fame_rating

async def get_suggested_profiles(
    db: AsyncSession,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_fame: Optional[float] = None,
    max_fame: Optional[float] = None,
    max_distance: Optional[float] = None,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Get suggested profiles for a user based on various criteria
    """
    pass