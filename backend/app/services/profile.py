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
    # Get user's profile
    result = await db.execute(select(Profile).join(User).filter(Profile.user_id == user_id))
    user_profile = result.scalars().first()
    
    if not user_profile:
        return []
    
    # Get user's gender and sexual preference
    user_gender = user_profile.gender
    user_preference = user_profile.sexual_preference
    
    # Get blocked users
    result = await db.execute(select(Block.blocked_id).filter(Block.blocker_id == user_profile.id))
    blocked_ids = [row[0] for row in result.all()]
    
    # Get users who blocked this user
    result = await db.execute(select(Block.blocker_id).filter(Block.blocked_id == user_profile.id))
    blocker_ids = [row[0] for row in result.all()]
    
    # Combine blocked and blocker IDs
    excluded_ids = blocked_ids + blocker_ids + [user_profile.id]
    
    # Base query for profiles
    query = select(Profile, User).join(User, Profile.user_id == User.id).filter(
        Profile.is_complete == True,
        Profile.id.notin_(excluded_ids)
    )
    
    # Add gender and sexual preference filters
    if user_gender and user_preference:
        if user_preference == SexualPreference.HETEROSEXUAL:
            # Heterosexual: match with opposite gender
            opposite_gender = Gender.FEMALE if user_gender == Gender.MALE else Gender.MALE
            query = query.filter(Profile.gender == opposite_gender)
            # And the other user should be interested in user's gender
            query = query.filter(or_(
                Profile.sexual_preference == SexualPreference.HOMOSEXUAL,
                Profile.sexual_preference == SexualPreference.BISEXUAL
            ))
        elif user_preference == SexualPreference.BISEXUAL:
            # Bisexual: no gender filter, but other user should be interested
            query = query.filter(or_(
                # If other is heterosexual, they should be opposite gender
                and_(
                    Profile.sexual_preference == SexualPreference.HETEROSEXUAL,
                    Profile.gender != user_gender
                ),
                # If other is homosexual, they should be same gender
                and_(
                    Profile.sexual_preference == SexualPreference.HOMOSEXUAL,
                    Profile.gender == user_gender
                ),
                # If other is bisexual, no restrictions
                Profile.sexual_preference == SexualPreference.BISEXUAL
            ))
    
    # Add age filters if provided
    if min_age or max_age:
        current_year = datetime.utcnow().year
        
        if min_age:
            max_birth_year = current_year - min_age
            # This would require a birth_year field in the profile, which is not in our schema
            # Alternative: use a calculated field or separate birth date field
    
        if max_age:
            min_birth_year = current_year - max_age
            # Similarly, would need birth_year or birth date field
    
    # Add fame rating filters
    if min_fame is not None:
        query = query.filter(Profile.fame_rating >= min_fame)
    
    if max_fame is not None:
        query = query.filter(Profile.fame_rating <= max_fame)
    
    # Add geographical distance filter
    if max_distance is not None and user_profile.latitude and user_profile.longitude:
        # This would require a geographic distance calculation
        # For simplicity in this implementation, we'll use a bounding box approximation
        # A more accurate implementation would use the Haversine formula or PostGIS
        
        # Convert distance (km) to approximate degrees
        # 1 degree latitude ~ 111 km
        # 1 degree longitude ~ 111 km * cos(latitude)
        lat_distance = max_distance / 111.0
        lng_distance = max_distance / (111.0 * cos(user_profile.latitude * 3.14159 / 180.0))
        
        query = query.filter(
            Profile.latitude.between(user_profile.latitude - lat_distance, user_profile.latitude + lat_distance),
            Profile.longitude.between(user_profile.longitude - lng_distance, user_profile.longitude + lng_distance)
        )
    
    # Add tag filters
    if tags and len(tags) > 0:
        # This requires a more complex query with joins to the tag tables
        # For simplicity, we'll retrieve all profiles and filter in memory
        
        # Get tag IDs
        tag_query = select(Tag.id).filter(func.lower(Tag.name).in_([t.lower() for t in tags]))
        result = await db.execute(tag_query)
        tag_ids = [row[0] for row in result.all()]
        
        if tag_ids:
            # For each tag, join to the profile_tags table
            for tag_id in tag_ids:
                query = query.filter(
                    Profile.id.in_(
                        select(profile_tags.c.profile_id).filter(profile_tags.c.tag_id == tag_id)
                    )
                )
    
    # Execute query with pagination
    result = await db.execute(query.offset(offset).limit(limit))
    profiles_with_users = result.all()
    
    # Calculate distance and common tags for each profile
    suggested_profiles = []
    for profile, user in profiles_with_users:
        # Calculate distance if coordinates available
        distance = None
        if user_profile.latitude and user_profile.longitude and profile.latitude and profile.longitude:
            # Simple Euclidean distance (not accurate for geographic coordinates)
            # A more accurate implementation would use the Haversine formula
            lat_diff = user_profile.latitude - profile.latitude
            lng_diff = user_profile.longitude - profile.longitude
            distance = (lat_diff**2 + lng_diff**2)**0.5 * 111.0  # Rough km conversion
        
        # Calculate common tags
        user_tag_ids = [tag.id for tag in user_profile.tags]
        profile_tag_ids = [tag.id for tag in profile.tags]
        common_tags = len(set(user_tag_ids).intersection(set(profile_tag_ids)))
        
        # Check if user has liked this profile
        result = await db.execute(
            select(Like).filter(Like.liker_id == user_profile.id, Like.liked_id == profile.id)
        )
        has_liked = result.scalars().first() is not None
        
        # Add to suggested profiles
        suggested_profiles.append({
            "profile": profile,
            "user": user,
            "distance": distance,
            "common_tags": common_tags,
            "has_liked": has_liked
        })
    
    # Sort by proximity first, then common tags, then fame rating
    suggested_profiles.sort(key=lambda x: (
        x["distance"] if x["distance"] is not None else float('inf'),
        -x["common_tags"],
        -x["profile"].fame_rating
    ))
    
    return suggested_profiles