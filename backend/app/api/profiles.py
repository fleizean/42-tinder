from ast import Delete
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from typing import Any, List, Optional
import uuid
import os
import shutil
from math import cos

from app.core.db import get_db
from app.core.security import get_current_user, get_current_verified_user
from app.core.config import settings
from app.models.user import User
from app.models.profile import Profile, Tag, Gender, SexualPreference
from app.schemas.profile import (
    Profile as ProfileSchema,
    ProfileUpdate,
    ProfileTagUpdate,
    Tag as TagSchema,
    ProfilePicture as ProfilePictureSchema,
    LocationUpdate,
    PublicProfile,
    TagUpdateSchema
)
from app.services.profile import (
    get_profile_by_user_id,
    is_profile_complete,
    update_profile,
    add_tag_to_profile,
    remove_tag_from_profile,
    update_profile_tags,
    add_profile_picture,
    remove_profile_picture,
    set_primary_picture,
    get_suggested_profiles,
    update_fame_rating
)
from app.services.interactions import visit_profile

router = APIRouter()

@router.get("/me", response_model=ProfileSchema)
async def get_my_profile(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Use selectinload to eagerly load relationships
    query = (
        select(Profile)
        .options(
            selectinload(Profile.pictures),
            selectinload(Profile.tags)
        )
        .filter(Profile.user_id == current_user.id)
    )
    
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile


@router.put("/me", response_model=ProfileSchema)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    try:
        # Get profile with relationships
        stmt = select(Profile).options(
            selectinload(Profile.pictures),
            selectinload(Profile.tags)
        ).where(Profile.user_id == current_user.id)
        
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Update profile fields
        for field, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)

        # Update is_complete status
        profile.is_complete = is_profile_complete(profile)
        
        # Save changes
        await db.commit()
        await db.refresh(profile)
        return profile

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/me/tags", response_model=ProfileSchema)
async def update_my_tags(
    tag_data: TagUpdateSchema,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    query = (
        select(Profile)
        .options(
            selectinload(Profile.tags),
            selectinload(Profile.pictures)
        )
        .filter(Profile.user_id == current_user.id)
    )
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil bulunamadı"
        )

    try:
        # Clear existing tags
        profile.tags = []
        
        # Add new tags
        for tag_name in tag_data.tags:
            # Check if tag already exists
            existing_tag_query = select(Tag).filter(Tag.name == tag_name)
            result = await db.execute(existing_tag_query)
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                # Use existing tag
                profile.tags.append(existing_tag)
            else:
                # Create new tag
                new_tag = Tag(name=tag_name)
                profile.tags.append(new_tag)
        
        await db.commit()
        await db.refresh(profile)
        
        return profile
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/me/location", response_model=ProfileSchema)
async def update_location(
    location: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    try:
        async with db.begin():
            # Get current profile with relationships loaded
            stmt = select(Profile).options(
                selectinload(Profile.pictures),
                selectinload(Profile.tags)
            ).where(Profile.user_id == current_user.id)
            
            result = await db.execute(stmt)
            profile = result.scalar_one_or_none()

            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )

            # Update location
            profile.latitude = location.latitude
            profile.longitude = location.longitude
            
            await db.commit()
            
            # Return updated profile with relationships
            return profile

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/me/pictures", response_model=ProfilePictureSchema)
async def upload_profile_picture(
    is_primary: bool = Form(False),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Upload a profile picture
    """
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Validate file type
    allowed_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.MEDIA_ROOT, "profile_pictures", str(profile.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Add picture to profile
    picture = await add_profile_picture(db, profile.id, file_path, is_primary)
    if not picture:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of pictures reached (5)"
        )
    
    return picture


@router.delete("/me/pictures/{picture_id}", response_model=dict)
async def delete_profile_picture(
    picture_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a profile picture
    """
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    result = await remove_profile_picture(db, profile.id, picture_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Picture not found"
        )
    
    return {
        "message": "Picture deleted successfully"
    }


@router.put("/me/pictures/{picture_id}/primary", response_model=dict)
async def set_primary_profile_picture(
    picture_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Set a picture as primary profile picture
    """
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    result = await set_primary_picture(db, profile.id, picture_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Picture not found"
        )
    
    return {
        "message": "Primary picture updated successfully"
    }


@router.get("/suggested", response_model=List[PublicProfile])
async def get_suggested(
    limit: int = 20,
    offset: int = 0,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_fame: Optional[float] = None,
    max_fame: Optional[float] = None,
    max_distance: Optional[float] = None,
    tags: Optional[List[str]] = None,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get suggested profiles
    """
    # Get user's profile
    profile = await get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Check if profile is complete
    if not profile.is_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete your profile first"
        )
    
    # Get suggested profiles
    suggested = await get_suggested_profiles(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        min_age=min_age,
        max_age=max_age,
        min_fame=min_fame,
        max_fame=max_fame,
        max_distance=max_distance,
        tags=tags
    )
    
    # Extract profiles
    profiles = []
    for item in suggested:
        profile_data = item["profile"]
        user_data = item["user"]
        
        # Combine profile and user data for public profile
        public_profile = PublicProfile(
            id=profile_data.id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            gender=profile_data.gender,
            sexual_preference=profile_data.sexual_preference,
            biography=profile_data.biography,
            latitude=profile_data.latitude,
            longitude=profile_data.longitude,
            fame_rating=profile_data.fame_rating,
            is_online=user_data.is_online,
            last_online=user_data.last_online,
            pictures=profile_data.pictures,
            tags=profile_data.tags
        )
        
        profiles.append(public_profile)
    
    return profiles


@router.get("/{profile_id}", response_model=PublicProfile)
async def get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a profile by ID
    """
    # Get user's profile
    user_profile = await get_profile_by_user_id(db, current_user.id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your profile not found"
        )
    
    # Get requested profile
    result = await db.execute(
        select(Profile, User)
        .join(User, Profile.user_id == User.id)
        .filter(Profile.id == profile_id)
    )
    profile_data = result.first()
    
    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile, user = profile_data
    
    # Record visit
    if user_profile.id != profile_id:  # Don't record visits to own profile
        await visit_profile(db, user_profile.id, profile_id)
    
    # Create public profile
    public_profile = PublicProfile(
        id=profile.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=profile.gender,
        sexual_preference=profile.sexual_preference,
        biography=profile.biography,
        latitude=profile.latitude,
        longitude=profile.longitude,
        fame_rating=profile.fame_rating,
        is_online=user.is_online,
        last_online=user.last_online,
        pictures=profile.pictures,
        tags=profile.tags,
        birth_date=user.birth_date
    )
    
    return public_profile